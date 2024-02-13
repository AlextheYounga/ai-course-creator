export type Topic = {
    id: Number;
    name: String;
    slug: String;
    outline_count?: Number;
    created_at?: Date | String;
    updated_at?: Date | String;
}


export type Outline = {
    id: Number;
    topic_id: Number;
    name: String | undefined;
    hash: String;
    skills: JSON | undefined;
    master_outline: JSON | undefined;
    file_path: String | undefined;
    created_at?: Date | String;
    updated_at?: Date | String;
}

export type Course = {
    id: Number;
    topic_id: Number;
    name: String;
    slug: String;
    level: Number;
    outline: JSON | undefined;
    meta: JSON | undefined;
    skill_challenge_chapter: String | undefined;
    skill_challenge_total_questions: Number | undefined;
    generated: Boolean;
    created_at?: Date | String;
    updated_at?: Date | String;
}


export type Chapter = {
    id: Number;
    topic_id: Number;
    course_slug: String;
    name: String;
    slug: String;
    outline: JSON | undefined;
    content_type: String | undefined;
    position: Number;
    created_at?: Date | String;
    updated_at?: Date | String;
}

export type Page = {
    id: Number;
    topic_id: Number;
    course_slug: String;
    chapter_slug: String;
    name: String;
    slug: String;
    permalink: String | undefined;
    link: String | undefined;
    path: String | undefined;
    hash: String | undefined;
    type: String | undefined;
    content: Text | undefined;
    summary: Text | undefined;
    nodes: JSON | undefined;
    position: Number;
    position_in_course: Number;
    position_in_series: Number;
    generated: Boolean;
    created_at?: Date | String;
    updated_at?: Date | String;
}

export type Prompt = {
    id: Number;
    model: String;
    action: String;
    estimated_tokens: Number;
    content: String;
    payload: JSON | undefined;
    properties: JSON | undefined;
    created_at?: Date | String;
    updated_at?: Date | String;
}

export type Response = {
    id: Number;
    prompt_id: Number;
    role: String;
    model: String;
    completion_tokens: Number;
    prompt_tokens: Number;
    total_tokens: Number;
    content: String;
    payload: JSON | undefined
    properties: JSON | undefined;
    created_at?: Date | String;
    updated_at?: Date | String;
}