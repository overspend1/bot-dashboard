/**
 * Status badge component for displaying bot status.
 */

import { Badge } from "@/components/ui/badge";
import { BotStatus } from "@/types/bot";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: BotStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const getStatusConfig = (status: BotStatus) => {
    switch (status) {
      case BotStatus.RUNNING:
        return {
          variant: "default" as const,
          label: "Running",
          dotClass: "status-running",
        };
      case BotStatus.STOPPED:
        return {
          variant: "secondary" as const,
          label: "Stopped",
          dotClass: "status-stopped",
        };
      case BotStatus.CRASHED:
        return {
          variant: "destructive" as const,
          label: "Crashed",
          dotClass: "status-crashed",
        };
      case BotStatus.STARTING:
        return {
          variant: "outline" as const,
          label: "Starting",
          dotClass: "status-starting",
        };
      case BotStatus.STOPPING:
        return {
          variant: "outline" as const,
          label: "Stopping",
          dotClass: "status-stopping",
        };
      default:
        return {
          variant: "secondary" as const,
          label: "Unknown",
          dotClass: "status-stopped",
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <Badge variant={config.variant} className={cn("gap-1.5", className)}>
      <span className={cn("status-dot", config.dotClass)} />
      {config.label}
    </Badge>
  );
}
