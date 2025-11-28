/**
 * Capsule Catalog Page
 * Week 8: White-Label Platform
 * Showcase all 27 capsule categories with filtering and search
 */

import { useState, useMemo } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import {
  getAllCategories,
  searchCategories,
  type CapsuleCategoryMetadata,
} from '../types/capsule-taxonomy';
import { Search, Filter, Grid3x3, List } from 'lucide-react';

const SERVICE_FAMILIES = [
  'All',
  'ThermalSampler',
  'WorldModel',
  'SimulatedSnapshot',
  'MicroAdaptEdge',
  'EnergyAtlas',
  'ProofEconomy',
  'DACOrchestrator',
  'A2AHostAgent',
];

export default function CapsuleCatalog() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFamily, setSelectedFamily] = useState('All');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const filteredCategories = useMemo(() => {
    let categories = searchQuery
      ? searchCategories(searchQuery)
      : getAllCategories();

    if (selectedFamily !== 'All') {
      categories = categories.filter(cat => cat.serviceFamily === selectedFamily);
    }

    return categories;
  }, [searchQuery, selectedFamily]);

  const categoryCount = filteredCategories.length;

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Capsule Catalog</h1>
            <p className="text-muted-foreground mt-2">
              27 Strategic Service Families - Complete Industriverse Taxonomy
            </p>
          </div>
          <Button variant="outline" onClick={() => window.history.back()}>
            ← Back
          </Button>
        </div>

        {/* Filters */}
        <Card className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search categories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Service Family Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <select
                value={selectedFamily}
                onChange={(e) => setSelectedFamily(e.target.value)}
                className="px-3 py-2 bg-background border border-border rounded-md text-sm"
              >
                {SERVICE_FAMILIES.map(family => (
                  <option key={family} value={family}>{family}</option>
                ))}
              </select>
            </div>

            {/* View Mode Toggle */}
            <div className="flex gap-1 border border-border rounded-md p-1">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3x3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4 text-sm text-muted-foreground">
            Showing {categoryCount} of 27 categories
          </div>
        </Card>

        {/* Categories */}
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCategories.map(category => (
              <CategoryCard key={category.id} category={category} />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredCategories.map(category => (
              <CategoryListItem key={category.id} category={category} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {categoryCount === 0 && (
          <Card className="p-12 text-center">
            <p className="text-muted-foreground">
              No categories found matching your criteria
            </p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => {
                setSearchQuery('');
                setSelectedFamily('All');
              }}
            >
              Clear Filters
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}

function CategoryCard({ category }: { category: CapsuleCategoryMetadata }) {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
      <div className="flex items-start gap-4">
        <div
          className="text-4xl p-3 rounded-lg"
          style={{ backgroundColor: `${category.color}20` }}
        >
          {category.icon}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold">{category.name}</h3>
          <Badge variant="outline" className="mt-1 text-xs">
            {category.serviceFamily}
          </Badge>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mt-4 line-clamp-2">
        {category.description}
      </p>

      <div className="mt-4 space-y-2">
        <div className="text-xs font-semibold text-muted-foreground">
          Widget:
        </div>
        <code className="text-xs bg-muted px-2 py-1 rounded">
          {category.whiteLabelWidget}
        </code>
      </div>

      <div className="mt-4 space-y-2">
        <div className="text-xs font-semibold text-muted-foreground">
          Examples:
        </div>
        <div className="flex flex-wrap gap-1">
          {category.examples.slice(0, 3).map((example, idx) => (
            <Badge key={idx} variant="secondary" className="text-xs">
              {example}
            </Badge>
          ))}
        </div>
      </div>
    </Card>
  );
}

function CategoryListItem({ category }: { category: CapsuleCategoryMetadata }) {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
      <div className="flex items-start gap-6">
        <div
          className="text-4xl p-3 rounded-lg flex-shrink-0"
          style={{ backgroundColor: `${category.color}20` }}
        >
          {category.icon}
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold">{category.name}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {category.description}
              </p>
            </div>
            <Badge variant="outline">
              {category.serviceFamily}
            </Badge>
          </div>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-xs font-semibold text-muted-foreground mb-2">
                Widget Component:
              </div>
              <code className="text-xs bg-muted px-2 py-1 rounded">
                {category.whiteLabelWidget}
              </code>
            </div>

            <div>
              <div className="text-xs font-semibold text-muted-foreground mb-2">
                Use Cases:
              </div>
              <div className="flex flex-wrap gap-1">
                {category.examples.map((example, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {example}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
