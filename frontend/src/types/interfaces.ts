export interface Listing {
    id: number;
    seller: string;
    record_price: number;
    media_condition: string;
    kept: boolean;
    evaluated: boolean;
    record: Record;
    score: number;
}

export interface Record {
    id: number;
    artist: string;
    title: string;
    format: string;
    label: string;
    catno: string;
    wants: number;
    haves: number;
    genres: string[];
    styles: string[];
    year: number;
    suggested_price: number;
    
}

export interface SellerGroup {
    seller: string;
    totalScore: number;
    records: Record[];
}

