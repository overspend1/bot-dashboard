/**
 * Type definitions for bot-related entities.
 */

export enum BotType {
  TELEGRAM_USERBOT = "telegram_userbot",
  TELEGRAM_BOT = "telegram_bot",
  DISCORD_BOT = "discord_bot",
}

export enum BotStatus {
  STOPPED = "stopped",
  STARTING = "starting",
  RUNNING = "running",
  STOPPING = "stopping",
  CRASHED = "crashed",
}

export interface Bot {
  id: string;
  name: string;
  type: BotType;
  config: Record<string, any>;
  status: BotStatus;
  auto_restart: boolean;
  created_at: string;
  updated_at: string;
  last_started_at: string | null;
  process_id: number | null;
  restart_count: number;
  last_crash_at: string | null;
}

export interface BotCreate {
  name: string;
  type: BotType;
  config: Record<string, any>;
  auto_restart: boolean;
}

export interface BotUpdate {
  name?: string;
  config?: Record<string, any>;
  auto_restart?: boolean;
}

export interface BotListResponse {
  total: number;
  page: number;
  page_size: number;
  bots: Bot[];
}

export interface BotStatusResponse {
  id: string;
  name: string;
  status: BotStatus;
  process_id: number | null;
  uptime_seconds: number | null;
  last_started_at: string | null;
}
