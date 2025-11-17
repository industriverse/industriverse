/**
 * CapsuleFilters Component
 *
 * Search, filter, and sort controls for capsule list
 */
import { __assign } from "tslib";
import { Search, Filter, ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, } from '@/components/ui/select';
export default function CapsuleFilters(_a) {
    var filters = _a.filters, onFiltersChange = _a.onFiltersChange, totalCount = _a.totalCount, filteredCount = _a.filteredCount;
    var handleSearchChange = function (value) {
        onFiltersChange(__assign(__assign({}, filters), { search: value }));
    };
    var handleStatusChange = function (value) {
        onFiltersChange(__assign(__assign({}, filters), { status: value }));
    };
    var handlePriorityChange = function (value) {
        onFiltersChange(__assign(__assign({}, filters), { priority: value }));
    };
    var handleSortByChange = function (value) {
        onFiltersChange(__assign(__assign({}, filters), { sortBy: value }));
    };
    var toggleSortOrder = function () {
        onFiltersChange(__assign(__assign({}, filters), { sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc' }));
    };
    var handleReset = function () {
        onFiltersChange({
            search: '',
            status: 'all',
            priority: 'all',
            sortBy: 'timestamp',
            sortOrder: 'desc'
        });
    };
    var hasActiveFilters = filters.search !== '' ||
        filters.status !== 'all' ||
        filters.priority !== 'all' ||
        filters.sortBy !== 'timestamp' ||
        filters.sortOrder !== 'desc';
    return (<div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"/>
        <Input type="text" placeholder="Search capsules by title or source..." value={filters.search} onChange={function (e) { return handleSearchChange(e.target.value); }} className="pl-10"/>
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap gap-3 items-center">
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground"/>
          <Select value={filters.status} onValueChange={handleStatusChange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Status"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="dismissed">Dismissed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Priority Filter */}
        <Select value={filters.priority} onValueChange={handlePriorityChange}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Priority"/>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priority</SelectItem>
            <SelectItem value="P1">P1 - Critical</SelectItem>
            <SelectItem value="P2">P2 - High</SelectItem>
            <SelectItem value="P3">P3 - Medium</SelectItem>
            <SelectItem value="P4">P4 - Low</SelectItem>
            <SelectItem value="P5">P5 - Info</SelectItem>
          </SelectContent>
        </Select>

        {/* Sort Controls */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-4 w-4 text-muted-foreground"/>
          <Select value={filters.sortBy} onValueChange={handleSortByChange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Sort by"/>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="timestamp">Timestamp</SelectItem>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="status">Status</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={toggleSortOrder} className="px-3">
            {filters.sortOrder === 'asc' ? '↑' : '↓'}
          </Button>
        </div>

        {/* Reset Button */}
        {hasActiveFilters && (<Button variant="ghost" size="sm" onClick={handleReset} className="ml-auto">
            Reset Filters
          </Button>)}
      </div>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        {filteredCount === totalCount ? (<span>Showing all {totalCount} capsules</span>) : (<span>
            Showing {filteredCount} of {totalCount} capsules
          </span>)}
      </div>
    </div>);
}
//# sourceMappingURL=CapsuleFilters.jsx.map