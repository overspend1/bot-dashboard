/**
 * System statistics display component.
 */

"use client";

import { useSystemStats } from "@/lib/hooks/useStats";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Cpu, HardDrive, MemoryStick, Network } from "lucide-react";

export function SystemStats() {
  const { data: stats, isLoading } = useSystemStats();

  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="glass">
            <CardHeader className="pb-2">
              <div className="h-4 w-20 bg-muted animate-pulse rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="glass">
        <CardHeader className="pb-2">
          <CardDescription className="flex items-center gap-2">
            <Cpu className="h-4 w-4" />
            CPU Usage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.cpu_percent.toFixed(1)}%</div>
          <div className="mt-2 h-2 w-full bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${Math.min(stats.cpu_percent, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="glass">
        <CardHeader className="pb-2">
          <CardDescription className="flex items-center gap-2">
            <MemoryStick className="h-4 w-4" />
            RAM Usage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.ram_percent.toFixed(1)}%</div>
          <div className="text-sm text-muted-foreground">
            {stats.ram_used_mb.toFixed(0)} / {stats.ram_total_mb.toFixed(0)} MB
          </div>
          <div className="mt-2 h-2 w-full bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${Math.min(stats.ram_percent, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="glass">
        <CardHeader className="pb-2">
          <CardDescription className="flex items-center gap-2">
            <HardDrive className="h-4 w-4" />
            Disk Usage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.disk_percent.toFixed(1)}%</div>
          <div className="text-sm text-muted-foreground">
            {stats.disk_used_gb.toFixed(1)} / {stats.disk_total_gb.toFixed(1)} GB
          </div>
          <div className="mt-2 h-2 w-full bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${Math.min(stats.disk_percent, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="glass">
        <CardHeader className="pb-2">
          <CardDescription className="flex items-center gap-2">
            <Network className="h-4 w-4" />
            Bots Status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Total:</span>
              <span className="font-mono">{stats.bots_total}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-green-500">Running:</span>
              <span className="font-mono">{stats.bots_running}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Stopped:</span>
              <span className="font-mono">{stats.bots_stopped}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-red-500">Crashed:</span>
              <span className="font-mono">{stats.bots_crashed}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
