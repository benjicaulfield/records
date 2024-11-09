export interface SearchResult {
    unique_tokens: string[];
    token_ids: number[];
    token_ids_with_context: number[];
    bpe_tokens: number[][];
    sampled_data: number[][];
    embeddings: { [key: string]: number[] };
    encoded_positions: [number, number][];
    extracted_info: ExtractedInfo[];
    chatgpt_output: string;
  }
  
  export interface ExtractedInfo {
    genres: string[];
    styles: string[];
    suggested_price: number;
    wants: number;
    haves: number;
    added: string;
  }