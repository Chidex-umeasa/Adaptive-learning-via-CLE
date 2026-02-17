export interface WebcamFeature {
  ts_ms: number;
  face_present: number;
  gaze_on_screen: number;
  gaze_dispersion: number;
  blink_rate: number;
  head_motion: number;
  away_events: number;
}

export interface Problem {
  id: string;
  title: string;
  description: string;
  difficulty: number;
  category: string;
  starter_code: string;
  hints: { id: string; text: string; level: number }[];
  test_cases: { input: any[]; expected: any }[];
  concepts: string[];
}

export interface ProblemListItem {
  id: string;
  title: string;
  difficulty: number;
  category: string;
}

export interface SubmissionResult {
  correct: boolean;
  tests_passed: number;
  tests_total: number;
  errors: string[];
  next_problem_id: string | null;
}

export interface LoadEstimate {
  load_score: number;
  label: string;
  confidence: number;
  recommended_action?: string;
}
