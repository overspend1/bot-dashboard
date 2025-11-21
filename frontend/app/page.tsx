/**
 * Main dashboard page.
 */

"use client";

import { useState } from "react";
import { useBots } from "@/lib/hooks/useBots";
import { SystemStats } from "@/components/dashboard/SystemStats";
import { BotGrid } from "@/components/dashboard/BotGrid";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Search, RefreshCw } from "lucide-react";
import { BotStatus } from "@/types/bot";

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<BotStatus | undefined>();

  const { data: botsData, isLoading, refetch } = useBots({
    search: search || undefined,
    status: statusFilter,
  });

  const handleRefresh = () => {
    refetch();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Bot Management Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Manage your Telegram and Discord bots
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button onClick={handleRefresh} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Bot
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* System Stats */}
        <section>
          <SystemStats />
        </section>

        {/* Bots Section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Your Bots</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search bots..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>
              <select
                value={statusFilter || ""}
                onChange={(e) =>
                  setStatusFilter(e.target.value as BotStatus | undefined)
                }
                className="h-9 px-3 rounded-md border border-input bg-background text-sm"
              >
                <option value="">All Status</option>
                <option value="running">Running</option>
                <option value="stopped">Stopped</option>
                <option value="crashed">Crashed</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="h-64 bg-card border border-border rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : (
            <BotGrid
              bots={botsData?.bots || []}
              onViewLogs={(bot) => {
                // Navigate to logs page
                window.location.href = `/bots/${bot.id}/logs`;
              }}
            />
          )}

          {!isLoading && botsData && (
            <div className="mt-4 text-sm text-muted-foreground text-center">
              Showing {botsData.bots.length} of {botsData.total} bots
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-sm text-muted-foreground text-center">
            Bot Management Dashboard v1.0.0
          </p>
        </div>
      </footer>
    </div>
  );
}
