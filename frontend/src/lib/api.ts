const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not configured");
}

export interface AnalysisRequest {
  repository_url: string;
}

export type AnalysisStatusValue =
  | "queued"
  | "running"
  | "completed"
  | "failed";

export interface AnalysisResponse {
  analysis_id: string;
  status: AnalysisStatusValue;
  message: string;
}

export interface Finding {
  category: string;
  severity:
  | "critical"
  | "high"
  | "medium"
  | "low"
  | "info";
  title: string;
  file: string | null;
  line: number | null;
  description: string;
  recommendation: string;
}

export interface AnalysisSummary {
  total_findings: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface AnalysisReport {
  summary: AnalysisSummary;
  executive_summary: string;
  findings: Finding[];
  recommendations: string[];
}

export interface AnalysisResult {
  repository: {
    owner: string;
    name: string;
    default_branch: string;
    language: string | null;
    stars: number;
    forks: number;
  };
  repository_id: string;
  file_count: number;
  document_count: number;
  chunk_count: number;
  embedding_count: number;
  analysis_time_seconds: number;
  report: AnalysisReport;
}

export interface AnalysisStatus {
  analysis_id: string;
  status: AnalysisStatusValue;
  stage: string;
  progress: number;
  message: string;
  result: AnalysisResult | null;
  error: string | null;
}

export async function createAnalysis(
  repositoryUrl: string,
): Promise<AnalysisResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/analyses`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repository_url: repositoryUrl,
      }),
    },
  );

  if (!response.ok) {
    const data = await response.json().catch(() => null);

    throw new Error(
      data?.detail || "Failed to start analysis",
    );
  }

  return response.json();
}

export async function getAnalysis(
  analysisId: string,
): Promise<AnalysisStatus> {
  const response = await fetch(
    `${API_URL}/api/v1/analyses/${analysisId}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const data = await response.json().catch(() => null);

    throw new Error(
      data?.detail || "Failed to fetch analysis",
    );
  }

  return response.json();
}