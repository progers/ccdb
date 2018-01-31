#ifndef FilterCoverage_h
#define FilterCoverage_h

#include <string>
#include <vector>

extern "C" void __llvm_profile_set_filename(const char* name);
extern "C" int __llvm_profile_write_file(void);
extern "C" uint64_t *__llvm_profile_begin_counters(void);
extern "C" uint64_t *__llvm_profile_end_counters(void);

// Utility functions for recording code coverage for a specific region of code.
// This should be used in conjunction with LLVM's source-based code coverage:
// https://clang.llvm.org/docs/SourceBasedCodeCoverage.html
//
// Basic usage:
//    functionA();
//    FilterCoverage::beginFilteringCoverage();
//    functionB();
//    FilterCoverage::endFilteringCoverage();
//    functionC();
// Only functionB will record code coverage which will be written to
// LLVM_PROFILE_FILE. Any remaining, unfiltered, coverage will be written to
// LLVM_PROFILE_FILE + _unfiltered.
//
// A helper object, FilterCoverage::Scope, can be used to ensure recursive
// functions record filtered coverage for the first and all nested calls. For
// more information, see the comment above FilterCoverage::Scope, below.
namespace FilterCoverage {

// Return the path where coverage will be written.
// TODO(phil): Should %m be specified to use merging so filtering can be run
// several times? Using a simple filename, only the last filtered coverage
// will be written.
static std::basic_string<char> coverageProfileOutputFilename() {
  const char* profileFileEnv = std::getenv("LLVM_PROFILE_FILE");
  if (!profileFileEnv || !profileFileEnv[0])
    return "default.profraw";
  return profileFileEnv;
}

// Coverage counters are used for the call counts of source regions. See:
// https://llvm.org/docs/CoverageMappingFormat.html#coverage-mapping-counter
// TODO(phil): Does saving counters correctly handle counter expressions?
// TODO(phil): Is there more coverage information than just the counters that
// needs to be saved?
typedef std::vector<uint64_t> CoverageCounters;

// Define a static local that is leaked. This will leak instead of requiring
// an exit-time destructor if -Wexit-time-destructors is used. See:
// https://chromium.googlesource.com/chromium/src/base/+/master/macros.h#70
#define __DEFINE_STATIC_LOCAL(type, name, arguments) \
  static type& name = *new type arguments

// Static storage for filtered counter data. This is stored so filtering can
// begin&end multiple times and the filtered counters will accumulate.
static CoverageCounters& filteredCounters() {
  __DEFINE_STATIC_LOCAL(CoverageCounters, filtered, ());
  return filtered;
}

// Static storage for the recorded unfiltered counter data. This is stored so
// the unfiltered counters can be restored after filtering.
static CoverageCounters& unfilteredCounters() {
  __DEFINE_STATIC_LOCAL(CoverageCounters, unfiltered, ());
  return unfiltered;
}

// Start recording filtered coverage.
static void beginFilteringCoverage() {
  uint64_t* begin = __llvm_profile_begin_counters();
  uint64_t* end = __llvm_profile_end_counters();

  // Save the current counters before filtering starts.
  unfilteredCounters().resize(end - begin);
  std::copy(begin, end, unfilteredCounters().begin());

  // Change the profile file to the filtered file. This should only be necessary
  // if the profile file was changed. This is done when beginning filtering in
  // case the program exits before filtering is explicitly ended.
  std::basic_string<char> profileFile = coverageProfileOutputFilename();
  __llvm_profile_set_filename(profileFile.c_str());

  // Initialize any new counters to 0. If no recorded filter coverage exists
  // yet, this initializes all counters to 0.
  filteredCounters().resize(end - begin, 0);

  // Copy previously recorded filtered counters so that filtered coverage
  // accumulates.
  std::copy(filteredCounters().begin(), filteredCounters().end(), begin);
}

// Stop recording filtered coverage and write the filtered coverage to a file.
// The coverage filename will be changed so any remaining coverage will be
// written to a different file with "_unfiltered" appended.
static void endFilteringCoverage() {
  // Write the filtered coverage.
  __llvm_profile_write_file();

  uint64_t* begin = __llvm_profile_begin_counters();
  uint64_t* end = __llvm_profile_end_counters();

  // Save the filtered counters so future filtering can accumulate.
  filteredCounters().resize(end - begin);
  std::copy(begin, end, filteredCounters().begin());

  // Change the profile file to [*.profraw]_unfiltered so any remaining,
  // unfiltered, coverage will get written to a different file.
  std::basic_string<char> profileFile = coverageProfileOutputFilename();
  profileFile.append("_unfiltered");
  __llvm_profile_set_filename(profileFile.c_str());

  // Restore the coverage before filtering.
  unfilteredCounters().resize(end - begin, 0);
  std::copy(unfilteredCounters().begin(), unfilteredCounters().end(), begin);
}


// Helper object for recording coverage in recursive functions. Coverage will
// only be started/ended for the first instantiation of this Scope. This ensures
// coverage will be recorded for all nested calls.
// Basic usage:
//    void recursiveFunction() {
//      FilterCoverage::Scope scope;
//      ...
//      recursiveFunction();
//    }
class Scope {
public:
  Scope() : filtering_(false) {
    // Do not record coverage if there is already an active scope recording.
    if (activeFilteringScope())
      return;
    activeFilteringScope() = true;
    filtering_ = true;
    beginFilteringCoverage();
  }
  ~Scope() {
    if (!filtering_)
      return;
    endFilteringCoverage();
    activeFilteringScope() = false;
  }

private:
  // Static storage for whether a Scope object is actively recording.
  static bool& activeFilteringScope() {
    static bool active = false;
    return active;
  }
  // True if this object is recording filtered coverage.
  bool filtering_;
};

}

#endif  // FilterCoverage_h
