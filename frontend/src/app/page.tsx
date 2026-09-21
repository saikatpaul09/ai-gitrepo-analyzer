"use client";

import {
  useState,
  type FormEvent,
} from "react";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  LinearProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import {
  useAnalysis,
  useCreateAnalysis,
} from "@/hooks/useAnalysis";

import type {
  Finding,
} from "@/lib/api";

const stageLabels: Record<string, string> = {
  queued: "Queued",
  scanning: "Scanning repository",
  downloading: "Downloading repository files",
  chunking: "Preparing repository content",
  embedding: "Generating embeddings",
  indexing: "Indexing repository",
  ai_analysis: "Running AI analysis",
  completed: "Analysis completed",
  failed: "Analysis failed",
};

function severityColor(
  severity: Finding["severity"],
) {
  switch (severity) {
    case "critical":
      return "error";

    case "high":
      return "warning";

    case "medium":
      return "warning";

    case "low":
      return "info";

    default:
      return "default";
  }
}

export default function Home() {
  const [repositoryUrl, setRepositoryUrl] =
    useState("");

  const [analysisId, setAnalysisId] =
    useState<string | null>(null);

  const createAnalysisMutation =
    useCreateAnalysis();

  const analysisQuery =
    useAnalysis(analysisId);

  const analysis =
    analysisQuery.data;

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!repositoryUrl.trim()) {
      return;
    }

    setAnalysisId(null);

    const result =
      await createAnalysisMutation.mutateAsync(
        repositoryUrl.trim(),
      );

    setAnalysisId(result.analysis_id);
  };

  const isAnalyzing =
    Boolean(analysisId) &&
    analysis?.status !== "completed" &&
    analysis?.status !== "failed";

  const report =
    analysis?.result?.report;

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "#f7f8fa",
      }}
    >
      {/* Header */}

      <Box
        sx={{
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: "white",
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              height: 72,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <Typography
              variant="h6"
              sx={{ fontWeight: 700 }}
            >
              AI Engineering Analyzer
            </Typography>

            <Chip
              label="V1"
              size="small"
              variant="outlined"
            />
          </Box>
        </Container>
      </Box>

      <Container
        maxWidth="lg"
        sx={{ py: 7 }}
      >
        {/* Hero */}

        {!analysisId && (
          <Box
            sx={{
              maxWidth: 820,
              mx: "auto",
              textAlign: "center",
            }}
          >
            <Typography
              variant="h2"

              sx={{
                fontSize: {
                  xs: "2.5rem",
                  md: "4rem",
                },
                fontWeight: 700,
                letterSpacing: "-0.04em",
              }}
            >
              Understand your codebase
              with AI.
            </Typography>

            <Typography
              variant="h6"
              color="text.secondary"
              sx={{
                mt: 2,
                mb: 5,
                fontWeight: 400,
                lineHeight: 1.6,
              }}
            >
              Analyze a public GitHub repository
              for architecture, security, testing,
              dependencies, and Docker practices.
            </Typography>

            <Paper
              elevation={0}
              sx={{
                p: 3,
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 3,
                textAlign: "left",
              }}
            >
              <form onSubmit={handleSubmit}>
                <Stack spacing={2}>
                  <TextField
                    fullWidth
                    label="GitHub repository URL"
                    placeholder="https://github.com/owner/repository"
                    value={repositoryUrl}
                    onChange={(event) =>
                      setRepositoryUrl(
                        event.target.value,
                      )
                    }
                    disabled={
                      createAnalysisMutation.isPending
                    }
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={
                      !repositoryUrl.trim() ||
                      createAnalysisMutation.isPending
                    }
                    sx={{
                      py: 1.5,
                      fontWeight: 700,
                    }}
                  >
                    Analyze Repository
                  </Button>
                </Stack>
              </form>

              {createAnalysisMutation.isError && (
                <Alert
                  severity="error"
                  sx={{ mt: 2 }}
                >
                  {
                    createAnalysisMutation.error
                      .message
                  }
                </Alert>
              )}
            </Paper>
          </Box>
        )}

        {/* Analysis Progress */}

        {analysisId &&
          analysis &&
          analysis.status !== "completed" &&
          analysis.status !== "failed" && (
            <Box
              sx={{
                maxWidth: 760,
                mx: "auto",
              }}
            >
              <Card
                elevation={0}
                sx={{
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 3,
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Stack spacing={3}>
                    <Box>
                      <Typography
                        variant="h5"
                        sx={{ fontWeight: 700 }}
                      >
                        Analyzing repository
                      </Typography>

                      <Typography
                        color="text.secondary"
                        sx={{ mt: 0.5 }}
                      >
                        This may take a few minutes
                        for larger repositories.
                      </Typography>
                    </Box>

                    <Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography
                          variant="body2"
                          sx={{ fontWeight: 600 }}
                        >
                          {stageLabels[
                            analysis.stage
                          ] ||
                            analysis.stage}
                        </Typography>

                        <Typography
                          variant="body2"
                          color="text.secondary"
                        >
                          {analysis.progress}%
                        </Typography>
                      </Box>

                      <LinearProgress
                        variant="determinate"
                        value={analysis.progress}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                        }}
                      />
                    </Box>

                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2,
                        bgcolor: "grey.50",
                      }}
                    >
                      <Typography variant="body2">
                        {analysis.message}
                      </Typography>
                    </Paper>

                    <Typography
                      variant="caption"
                      color="text.secondary"
                    >
                      Analysis ID: {analysisId}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Box>
          )}

        {/* Failed */}

        {analysis?.status === "failed" && (
          <Box
            sx={{
              maxWidth: 760,
              mx: "auto",
            }}
          >
            <Alert
              severity="error"
              sx={{ mb: 3 }}
            >
              {analysis.error ||
                "Analysis failed."}
            </Alert>

            <Button
              variant="outlined"
              onClick={() => {
                setAnalysisId(null);
              }}
            >
              Try another repository
            </Button>
          </Box>
        )}

        {/* Report */}

        {analysis?.status === "completed" &&
          report && (
            <Box>
              <Stack spacing={4}>
                {/* Report header */}

                <Box>
                  <Typography
                    variant="overline"
                    color="text.secondary"
                    sx={{ fontWeight: 700 }}
                  >
                    Engineering Report
                  </Typography>

                  <Typography
                    variant="h3"
                    sx={{
                      mt: 0.5,
                      fontWeight: 800,
                      letterSpacing: "-0.03em",
                    }}
                  >
                    {analysis.result?.repository
                      .name}
                  </Typography>

                  <Typography
                    color="text.secondary"
                    sx={{ mt: 1 }}
                  >
                    {analysis.result?.repository
                      .owner}
                    {" / "}
                    {
                      analysis.result?.repository
                        .default_branch
                    }
                  </Typography>
                </Box>

                {/* Summary */}

                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: {
                      xs: "1fr 1fr",
                      md: "repeat(5, 1fr)",
                    },
                    gap: 2,
                  }}
                >
                  {[
                    [
                      "Critical",
                      report.summary.critical,
                      "error",
                    ],
                    [
                      "High",
                      report.summary.high,
                      "warning",
                    ],
                    [
                      "Medium",
                      report.summary.medium,
                      "warning",
                    ],
                    [
                      "Low",
                      report.summary.low,
                      "info",
                    ],
                    [
                      "Total",
                      report.summary
                        .total_findings,
                      "default",
                    ],
                  ].map(
                    ([label, value, color]) => (
                      <Card
                        key={label}
                        elevation={0}
                        sx={{
                          border: "1px solid",
                          borderColor:
                            "divider",
                          borderRadius: 3,
                        }}
                      >
                        <CardContent>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                          >
                            {label}
                          </Typography>

                          <Typography
                            variant="h4"
                            sx={{ mt: 1, fontWeight: 800 }}
                          >
                            {value}
                          </Typography>
                        </CardContent>
                      </Card>
                    ),
                  )}
                </Box>

                {/* Executive summary */}

                <Card
                  elevation={0}
                  sx={{
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 3,
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 700 }}
                    >
                      Executive Summary
                    </Typography>

                    <Typography
                      color="text.secondary"
                      sx={{
                        mt: 2,
                        lineHeight: 1.8,
                      }}
                    >
                      {
                        report.executive_summary
                      }
                    </Typography>
                  </CardContent>
                </Card>

                {/* Findings */}

                <Box>
                  <Typography
                    variant="h5"
                    sx={{ mb: 2, fontWeight: 700 }}
                  >
                    Findings
                  </Typography>

                  <Stack spacing={2}>
                    {report.findings.map(
                      (finding, index) => (
                        <Card
                          key={`${finding.title}-${index}`}
                          elevation={0}
                          sx={{
                            border: "1px solid",
                            borderColor:
                              "divider",
                            borderRadius: 3,
                          }}
                        >
                          <CardContent
                            sx={{ p: 3 }}
                          >
                            <Stack
                              spacing={2}
                            >
                              <Box
                                sx={{
                                  display:
                                    "flex",
                                  alignItems:
                                    "center",
                                  gap: 1,
                                  flexWrap:
                                    "wrap",
                                }}
                              >
                                <Chip
                                  label={
                                    finding.severity.toUpperCase()
                                  }
                                  size="small"
                                  color={
                                    severityColor(
                                      finding.severity,
                                    ) as
                                    | "error"
                                    | "warning"
                                    | "info"
                                    | "default"
                                  }
                                />

                                <Chip
                                  label={
                                    finding.category
                                  }
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>

                              <Typography
                                variant="h6"
                                sx={{ fontWeight: 700 }}
                              >
                                {finding.title}
                              </Typography>

                              {finding.file && (
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{
                                    fontFamily:
                                      "monospace",
                                  }}
                                >
                                  {finding.file}
                                  {finding.line
                                    ? `:${finding.line}`
                                    : ""}
                                </Typography>
                              )}

                              <Typography
                                color="text.secondary"
                                sx={{
                                  lineHeight: 1.7,
                                }}
                              >
                                {
                                  finding.description
                                }
                              </Typography>

                              <Divider />

                              <Box>
                                <Typography
                                  variant="subtitle2"
                                  sx={{ fontWeight: 700 }}
                                >
                                  Recommendation
                                </Typography>

                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{
                                    mt: 0.5,
                                    lineHeight: 1.7,
                                  }}
                                >
                                  {
                                    finding.recommendation
                                  }
                                </Typography>
                              </Box>
                            </Stack>
                          </CardContent>
                        </Card>
                      ),
                    )}

                    {report.findings.length ===
                      0 && (
                        <Alert severity="success">
                          No engineering issues were
                          identified by the analysis.
                        </Alert>
                      )}
                  </Stack>
                </Box>

                {/* Recommendations */}

                {report.recommendations.length >
                  0 && (
                    <Card
                      elevation={0}
                      sx={{
                        border: "1px solid",
                        borderColor:
                          "divider",
                        borderRadius: 3,
                      }}
                    >
                      <CardContent
                        sx={{ p: 4 }}
                      >
                        <Typography
                          variant="h6"
                          sx={{ fontWeight: 700 }}
                        >
                          Recommendations
                        </Typography>

                        <Stack
                          spacing={1.5}
                          sx={{ mt: 2 }}
                        >
                          {report.recommendations.map(
                            (
                              recommendation,
                              index,
                            ) => (
                              <Box
                                key={index}
                                sx={{
                                  display:
                                    "flex",
                                  gap: 1.5,
                                }}
                              >
                                <Typography sx={{ fontWeight: 700 }}>
                                  {index + 1}.
                                </Typography>

                                <Typography
                                  color="text.secondary"
                                >
                                  {
                                    recommendation
                                  }
                                </Typography>
                              </Box>
                            ),
                          )}
                        </Stack>
                      </CardContent>
                    </Card>
                  )}

                {/* Metadata */}

                <Paper
                  variant="outlined"
                  sx={{
                    p: 3,
                    borderRadius: 3,
                  }}
                >
                  <Stack
                    direction={{
                      xs: "column",
                      md: "row",
                    }}
                    spacing={3}
                  >
                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        Files
                      </Typography>

                      <Typography sx={{ fontWeight: 700 }}>
                        {
                          analysis.result
                            ?.file_count
                        }
                      </Typography>
                    </Box>

                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        Chunks
                      </Typography>

                      <Typography sx={{ fontWeight: 700 }}>
                        {
                          analysis.result
                            ?.chunk_count
                        }
                      </Typography>
                    </Box>

                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        Analysis time
                      </Typography>

                      <Typography sx={{ fontWeight: 700 }}>
                        {
                          analysis.result
                            ?.analysis_time_seconds
                        }
                        s
                      </Typography>
                    </Box>

                    <Box sx={{ ml: "auto" }}>
                      <Button
                        variant="outlined"
                        onClick={() => {
                          setAnalysisId(null);
                          setRepositoryUrl("");
                        }}
                      >
                        Analyze Another
                      </Button>
                    </Box>
                  </Stack>
                </Paper>
              </Stack>
            </Box>
          )}
      </Container>
    </Box>
  );
}