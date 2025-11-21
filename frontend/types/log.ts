/**
 * Type definitions for log entries.
 */

export enum LogLevel {
  DEBUG = "DEBUG",
  INFO = "INFO",
  WARNING = "WARNING",
  ERROR = "ERROR",
  CRITICAL = "CRITICAL",
}

export interface LogEntry {
  id: number;
  bot_id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
}

export interface LogListResponse {
  total: number;
  page: number;
  page_size: number;
  logs: LogEntry[];
}

export interface LogWebSocketMessage {
  timestamp: string;
  level: string;
  message: string;
  type?: "ping";
}
