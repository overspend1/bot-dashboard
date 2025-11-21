/**
 * Hooks for fetching and managing bots.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api/client";
import type {
  Bot,
  BotListResponse,
  BotCreate,
  BotUpdate,
  BotStatusResponse,
} from "@/types/bot";
import type { BotFilters } from "@/types/api";

/**
 * Hook to fetch list of bots with optional filters.
 */
export function useBots(filters?: BotFilters) {
  return useQuery({
    queryKey: ["bots", filters],
    queryFn: async () => {
      const params = new URLSearchParams();

      if (filters?.status) {
        params.append("status", filters.status);
      }
      if (filters?.search) {
        params.append("search", filters.search);
      }
      if (filters?.page) {
        params.append("page", filters.page.toString());
      }
      if (filters?.page_size) {
        params.append("page_size", filters.page_size.toString());
      }

      const response = await apiClient.get<BotListResponse>(
        `/bots?${params.toString()}`
      );
      return response.data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  });
}

/**
 * Hook to fetch a single bot by ID.
 */
export function useBot(botId: string) {
  return useQuery({
    queryKey: ["bots", botId],
    queryFn: async () => {
      const response = await apiClient.get<Bot>(`/bots/${botId}`);
      return response.data;
    },
    enabled: !!botId,
  });
}

/**
 * Hook to fetch bot status.
 */
export function useBotStatus(botId: string) {
  return useQuery({
    queryKey: ["bots", botId, "status"],
    queryFn: async () => {
      const response = await apiClient.get<BotStatusResponse>(
        `/bots/${botId}/status`
      );
      return response.data;
    },
    refetchInterval: 5000,
    enabled: !!botId,
  });
}

/**
 * Hook to create a new bot.
 */
export function useCreateBot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botData: BotCreate) => {
      const response = await apiClient.post<Bot>("/bots", botData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}

/**
 * Hook to update a bot.
 */
export function useUpdateBot(botId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botData: BotUpdate) => {
      const response = await apiClient.put<Bot>(`/bots/${botId}`, botData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bots", botId] });
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}

/**
 * Hook to delete a bot.
 */
export function useDeleteBot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botId: string) => {
      await apiClient.delete(`/bots/${botId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}

/**
 * Hook to start a bot.
 */
export function useStartBot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botId: string) => {
      const response = await apiClient.post<Bot>(`/bots/${botId}/start`);
      return response.data;
    },
    onSuccess: (_, botId) => {
      queryClient.invalidateQueries({ queryKey: ["bots", botId] });
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}

/**
 * Hook to stop a bot.
 */
export function useStopBot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botId: string) => {
      const response = await apiClient.post<Bot>(`/bots/${botId}/stop`);
      return response.data;
    },
    onSuccess: (_, botId) => {
      queryClient.invalidateQueries({ queryKey: ["bots", botId] });
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}

/**
 * Hook to restart a bot.
 */
export function useRestartBot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (botId: string) => {
      const response = await apiClient.post<Bot>(`/bots/${botId}/restart`);
      return response.data;
    },
    onSuccess: (_, botId) => {
      queryClient.invalidateQueries({ queryKey: ["bots", botId] });
      queryClient.invalidateQueries({ queryKey: ["bots"] });
    },
  });
}
