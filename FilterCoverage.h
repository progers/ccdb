#ifndef FilterCoverage_h
#define FilterCoverage_h

#include <memory>
#include <string>
#include <vector>
#include <string.h>

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

struct BeforeFilteringData {
  // Saved counters from before filtering.
  std::vector<uint64_t> counters;

  // TODO(phil): Is there more coverage information than just the counters that
  // needs to be saved?
};

// Start recording filtered coverage. If |beforeData| is passed, record the
// coverage counters before filtering begins.
static void beginFilteringCoverage(BeforeFilteringData* beforeData = nullptr) {
  uint64_t* begin = __llvm_profile_begin_counters();
  uint64_t* end = __llvm_profile_end_counters();

  if (beforeData) {
    // Save the current coverage counters before filtering starts.
    beforeData->counters.resize(end - begin);
    std::copy(begin, end, beforeData->counters.begin());
  }

  // Change the profile file to the filtered file. This should only be necessary
  // if the profile file was changed. This is done when starting filtering in
  // case the program exits before filtering is ended.
  auto profileFile = FilterCoverage::coverageProfileOutputFilename();
  __llvm_profile_set_filename(profileFile.c_str());

  // Reset the coverage counters to 0.
  memset(begin, 0, sizeof(uint64_t) * (end - begin));
}

// Stop recording filtered coverage and write the filtered coverage to a file.
// If |beforeData| is passed, restore the counters from before filtering.
static void endFilteringCoverage(const BeforeFilteringData* beforeData = nullptr) {
  // Write the filtered coverage.
  __llvm_profile_write_file();

  // Change the profile file to [*.profraw]_unfiltered so any remaining coverage
  // will get written to a different file.
  auto unfilteredProfileFile = FilterCoverage::coverageProfileOutputFilename();
  unfilteredProfileFile.append("_unfiltered");
  __llvm_profile_set_filename(unfilteredProfileFile.c_str());

  if (beforeData) {
    // Restore the coverage before filtering.
    std::copy(beforeData->counters.begin(), beforeData->counters.end(),
              __llvm_profile_begin_counters());
  }
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
  Scope() : filtering_(nullptr) {
    // Do not record coverage if there is already an active scope recording.
    if (activeScopeData())
      return;

    // Create storage for the initial filter data and begin filtering. Other
    // scopes will not be active while |activeScopeData| is non-null.
    activeScopeData() = std::unique_ptr<BeforeFilteringData>(new BeforeFilteringData);
    filtering_ = activeScopeData().get();
    beginFilteringCoverage(filtering_);
  }
  ~Scope() {
    if (filtering_) {
      endFilteringCoverage(filtering_);
      activeScopeData() = nullptr;
    }
  }

private:
  // Define a static local that is leaked. This will leak instead of requiring
  // an exit-time destructor if -Wexit-time-destructors is used. See:
  // https://chromium.googlesource.com/chromium/src/base/+/master/macros.h#70
  #define _DEFINE_STATIC_LOCAL(type, name, arguments) \
    static type& name = *new type arguments
  // Static storage for the active Scope's initial filter data, or null if there
  // is no active filter scope.
  static std::unique_ptr<BeforeFilteringData>& activeScopeData() {
    _DEFINE_STATIC_LOCAL(std::unique_ptr<BeforeFilteringData>, active, ());
    return active;
  }
  // Initial filter data if this scope is actively recording, null otherwise.
  BeforeFilteringData* filtering_;
};

}

#endif  // FilterCoverage_h
