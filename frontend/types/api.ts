/**
 * Type definitions for API responses.
 */

export interface ApiError {
  detail: string;
  message?: string;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface BotFilters extends PaginationParams {
  status?: string;
  search?: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: ApiError;
  status: number;
}
