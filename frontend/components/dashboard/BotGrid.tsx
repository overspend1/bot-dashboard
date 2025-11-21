/**
 * Grid layout for bot cards.
 */

"use client";

import { Bot } from "@/types/bot";
import { BotCard } from "./BotCard";

interface BotGridProps {
  bots: Bot[];
  onViewLogs?: (bot: Bot) => void;
}

export function BotGrid({ bots, onViewLogs }: BotGridProps) {
  if (bots.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground text-lg">No bots found</p>
        <p className="text-muted-foreground text-sm mt-2">
          Create your first bot to get started
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {bots.map((bot) => (
        <BotCard key={bot.id} bot={bot} onViewLogs={onViewLogs} />
      ))}
    </div>
  );
}
