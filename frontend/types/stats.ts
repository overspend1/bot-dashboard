/**
 * Type definitions for statistics.
 */

export interface SystemStats {
  cpu_percent: number;
  ram_used_mb: number;
  ram_total_mb: number;
  ram_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_percent: number;
  network_sent_mb: number;
  network_recv_mb: number;
  bots_total: number;
  bots_running: number;
  bots_stopped: number;
  bots_crashed: number;
}

export interface BotStats {
  bot_id: string;
  bot_name: string;
  cpu_percent: number | null;
  ram_mb: number | null;
  uptime_seconds: number | null;
  status: string;
}

export interface AggregateStats {
  total_bots: number;
  total_cpu_percent: number;
  total_ram_mb: number;
  average_uptime_seconds: number | null;
  bot_stats: BotStats[];
}

export interface StatsWebSocketMessage {
  timestamp: string;
  system: SystemStats;
  bots: BotStats[];
}
