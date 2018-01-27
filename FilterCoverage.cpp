#include "FilterCoverage.h"

#include <cstdint>
#include <cstdlib> // getenv
#include <string.h> // memset

extern "C" void __llvm_profile_set_filename(const char* name);
extern "C" int __llvm_profile_write_file(void);
extern "C" uint64_t *__llvm_profile_begin_counters(void);
extern "C" uint64_t *__llvm_profile_end_counters(void);

bool FilterCoverageScope::preventNestedFilteredCoverage = false;

FilterCoverageScope::FilterCoverageScope() : recording_(false) {
  if (preventNestedFilteredCoverage)
    return;

  preventNestedFilteredCoverage = true;
  recording_ = true;

  // Save the current coverage counters before filtering starts.
  uint64_t* begin = __llvm_profile_begin_counters();
  uint64_t* end = __llvm_profile_end_counters();
  unfilteredCounters.resize(end - begin);
  std::copy(begin, end, unfilteredCounters.begin());

  // Calculate the filtered and unfiltered coverage files.
  const char* filteredProfileEnv = std::getenv("LLVM_PROFILE_FILE");
  if (!filteredProfileEnv || !filteredProfileEnv[0])
    filteredProfileFile = "default.profraw";
  else
    filteredProfileFile = filteredProfileEnv;
  unfilteredProfileFile = filteredProfileFile + "_unfiltered";

  // Change the profile file to the filtered file.
  __llvm_profile_set_filename(filteredProfileFile.c_str());

  // Reset the coverage counters to 0.
  memset(begin, 0, sizeof(uint64_t) * (end - begin));
}

FilterCoverageScope::~FilterCoverageScope() {
  if (!recording_)
    return;

  // Write the filtered coverage.
  __llvm_profile_write_file();

  // Change the profile file to the unfiltered file for any remaining coverage.
  __llvm_profile_set_filename(unfilteredProfileFile.c_str());

  // Restore the coverage before filtering.
  std::copy(unfilteredCounters.begin(), unfilteredCounters.end(),
            __llvm_profile_begin_counters());
}
