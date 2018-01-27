#ifndef FilterCoverage_h
#define FilterCoverage_h

#include <string>
#include <vector>

// Filter code coverage to only code within this object's scope.
//
// For example:
//
// functionA();
// {
//   FilterCoverageScope scope;
//   functionB();
// }
// functionC();
//
// Coverage will only be written for functionB.
class FilterCoverageScope {
 public:
  FilterCoverageScope();
  virtual ~FilterCoverageScope();

 private:
  // True if there is an active |FilterCoverageScope| recording which prevents
  // other filters from running.
  static bool preventNestedFilteredCoverage;

  // True if this scope object should record filtered coverage.
  bool recording_;

  // Saved counters from before the filter was active.
  std::vector<uint64_t> unfilteredCounters;
  // Filename for the filtered profile data output.
  std::basic_string<char> filteredProfileFile;
  // Filename for the unfiltered profile data output.
  std::basic_string<char> unfilteredProfileFile;
};

#endif  // FilterCoverage_h
