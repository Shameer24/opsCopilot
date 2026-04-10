export type AuthToken = {
  access_token: string;
  token_type: "bearer";
};

export type DocumentOut = {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
};

export type Citation = {
  chunk_id: string;
  document_id: string;
  filename: string;
  page_start?: number | null;
  page_end?: number | null;
  line_start?: number | null;
  line_end?: number | null;
  score: number;
};

export type AskResponse = {
  answer_markdown: string;
  citations: Citation[];
  query_log_id: string;
};