"use client";

import {
  useMutation,
  useQuery,
} from "@tanstack/react-query";

import {
  createAnalysis,
  getAnalysis,
} from "@/lib/api";

export function useCreateAnalysis() {
  return useMutation({
    mutationFn: createAnalysis,
  });
}

export function useAnalysis(
  analysisId: string | null,
) {
  return useQuery({
    queryKey: ["analysis", analysisId],

    queryFn: () => {
      if (!analysisId) {
        throw new Error("Analysis ID is required");
      }

      return getAnalysis(analysisId);
    },

    enabled: Boolean(analysisId),

    refetchInterval: (query) => {
      const status = query.state.data?.status;

      if (
        status === "completed" ||
        status === "failed"
      ) {
        return false;
      }

      return 2000;
    },
  });
}