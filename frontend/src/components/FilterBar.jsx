import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { MagnifyingGlass, SortAscending, X } from '@phosphor-icons/react'

export function FilterBar({
  searchQuery,
  onSearchChange,
  selectedHospital,
  onHospitalChange,
  selectedSentiment,
  onSentimentChange,
  hospitalNames,
  onClearFilters,
}) {
  const hasActiveFilters = searchQuery || selectedHospital !== 'all' || selectedSentiment !== 'all'

  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-3 md:space-y-0 md:flex md:items-center md:gap-3">
      <div className="relative flex-1">
        <MagnifyingGlass 
          size={18} 
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" 
        />
        <Input
          id="search-hospitals"
          placeholder="Search hospitals..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="flex gap-2 items-center">
        <SortAscending size={18} className="text-muted-foreground hidden md:block" />
        
        <Select value={selectedHospital} onValueChange={onHospitalChange}>
          <SelectTrigger id="filter-hospital" className="w-full md:w-[200px]">
            <SelectValue placeholder="All Hospitals" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Hospitals</SelectItem>
            {hospitalNames.map((name) => (
              <SelectItem key={name} value={name}>
                {name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedSentiment} onValueChange={onSentimentChange}>
          <SelectTrigger id="filter-sentiment" className="w-full md:w-[160px]">
            <SelectValue placeholder="All Sentiment" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sentiment</SelectItem>
            <SelectItem value="positive">Positive</SelectItem>
            <SelectItem value="negative">Negative</SelectItem>
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClearFilters}
            title="Clear filters"
            className="shrink-0"
          >
            <X size={18} />
          </Button>
        )}
      </div>
    </div>
  )
}
