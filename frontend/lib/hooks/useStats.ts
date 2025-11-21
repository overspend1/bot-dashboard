/**
 * Hooks for fetching statistics data.
 */

import { useQuery } from "@tanstack/react-query";
import apiClient from "@/lib/api/client";
import type { SystemStats, BotStats, AggregateStats } from "@/types/stats";

/**
 * Hook to fetch system statistics.
 */
export function useSystemStats() {
  return useQuery({
    queryKey: ["stats", "system"],
    queryFn: async () => {
      const response = await apiClient.get<SystemStats>("/stats/system");
      return response.data;
    },
    refetchInterval: 5000, // Refetch every 5 seconds
  });
}

/**
 * Hook to fetch bot statistics by bot ID.
 */
export function useBotStats(botId: string) {
  return useQuery({
    queryKey: ["stats", "bot", botId],
    queryFn: async () => {
      const response = await apiClient.get<BotStats>(`/stats/bots/${botId}`);
      return response.data;
    },
    refetchInterval: 5000,
    enabled: !!botId,
  });
}

/**
 * Hook to fetch aggregate statistics for all bots.
 */
export function useAggregateStats() {
  return useQuery({
    queryKey: ["stats", "bots", "aggregate"],
    queryFn: async () => {
      const response = await apiClient.get<AggregateStats>("/stats/bots");
      return response.data;
    },
    refetchInterval: 5000,
  });
}
