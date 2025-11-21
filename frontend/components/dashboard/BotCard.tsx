/**
 * Bot card component displaying bot information and controls.
 */

"use client";

import { Bot } from "@/types/bot";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "./StatusBadge";
import {
  Play,
  Square,
  RotateCw,
  Trash2,
  FileText,
  Cpu,
  MemoryStick,
  Clock,
} from "lucide-react";
import { formatUptime, formatRelativeTime } from "@/lib/utils";
import { useStartBot, useStopBot, useRestartBot, useDeleteBot } from "@/lib/hooks/useBots";
import { useState } from "react";

interface BotCardProps {
  bot: Bot;
  onViewLogs?: (bot: Bot) => void;
}

export function BotCard({ bot, onViewLogs }: BotCardProps) {
  const startBot = useStartBot();
  const stopBot = useStopBot();
  const restartBot = useRestartBot();
  const deleteBot = useDeleteBot();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleStart = () => {
    startBot.mutate(bot.id);
  };

  const handleStop = () => {
    stopBot.mutate(bot.id);
  };

  const handleRestart = () => {
    restartBot.mutate(bot.id);
  };

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${bot.name}"?`)) {
      setIsDeleting(true);
      deleteBot.mutate(bot.id, {
        onSettled: () => setIsDeleting(false),
      });
    }
  };

  const isRunning = bot.status === "running";
  const isStopped = bot.status === "stopped";
  const isLoading =
    startBot.isPending ||
    stopBot.isPending ||
    restartBot.isPending ||
    deleteBot.isPending;

  return (
    <Card className="glass hover:border-primary/50 transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{bot.name}</CardTitle>
            <p className="text-sm text-muted-foreground capitalize">
              {bot.type.replace(/_/g, " ")}
            </p>
          </div>
          <StatusBadge status={bot.status} />
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {isRunning && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Uptime:</span>
              <span className="font-mono">
                {bot.last_started_at
                  ? formatRelativeTime(bot.last_started_at)
                  : "N/A"}
              </span>
            </div>
            {bot.process_id && (
              <div className="flex items-center gap-2 text-sm">
                <Cpu className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">PID:</span>
                <span className="font-mono">{bot.process_id}</span>
              </div>
            )}
          </div>
        )}

        {bot.status === "crashed" && (
          <div className="text-sm text-destructive">
            Last crash: {formatRelativeTime(bot.last_crash_at)}
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <RotateCw className="h-4 w-4" />
          <span>Auto-restart: {bot.auto_restart ? "Enabled" : "Disabled"}</span>
        </div>
      </CardContent>

      <CardFooter className="gap-2 flex-wrap">
        {isStopped && (
          <Button
            size="sm"
            onClick={handleStart}
            disabled={isLoading}
            className="flex-1"
          >
            <Play className="h-4 w-4 mr-1" />
            Start
          </Button>
        )}

        {isRunning && (
          <>
            <Button
              size="sm"
              variant="destructive"
              onClick={handleStop}
              disabled={isLoading}
              className="flex-1"
            >
              <Square className="h-4 w-4 mr-1" />
              Stop
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleRestart}
              disabled={isLoading}
              className="flex-1"
            >
              <RotateCw className="h-4 w-4 mr-1" />
              Restart
            </Button>
          </>
        )}

        {!isRunning && bot.status !== "stopped" && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleRestart}
            disabled={isLoading}
            className="flex-1"
          >
            <RotateCw className="h-4 w-4 mr-1" />
            Restart
          </Button>
        )}

        <Button
          size="sm"
          variant="outline"
          onClick={() => onViewLogs?.(bot)}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-1" />
          Logs
        </Button>

        <Button
          size="sm"
          variant="ghost"
          onClick={handleDelete}
          disabled={isLoading || isDeleting}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
