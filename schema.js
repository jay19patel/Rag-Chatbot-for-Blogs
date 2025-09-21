import { z } from "zod";

const TextSection = z.object({
  title: z.string(),
  type: z.literal("text"),
  content: z.string(),
});

const BulletsSection = z.object({
  title: z.string(),
  type: z.literal("bullets"),
  items: z.array(z.string()),
});

const ImageSection = z.object({
  title: z.string(),
  type: z.literal("image"),
  url: z.string(),
  alt: z.string().optional(),
  caption: z.string().optional(),
});

const CodeSection = z.object({
  title: z.string(),
  type: z.literal("code"),
  language: z.string(),
  content: z.string(),
});

const TableSection = z.object({
  title: z.string(),
  type: z.literal("table"),
  headers: z.array(z.string()),
  rows: z.array(z.array(z.string())),
});

const NoteSection = z.object({
  title: z.string(),
  type: z.literal("note"),
  content: z.string(),
});

const YouTubeSection = z.object({
  title: z.string(),
  type: z.literal("youtube"),
  videoId: z.string(),
  description: z.string().optional(),
});

const LinksSection = z.object({
  title: z.string(),
  type: z.literal("links"),
  links: z.array(
    z.object({
      text: z.string(),
      url: z.string(),
      description: z.string().optional(),
    })
  ),
});

const Section = z.union([
  TextSection,
  BulletsSection,
  ImageSection,
  CodeSection,
  TableSection,
  NoteSection,
  YouTubeSection,
  LinksSection,
]);

const Content = z.object({
  introduction: z.string(),
  sections: z.array(Section),
  conclusion: z.string(),
});

const Blog = z.object({
  id: z.number(),
  slug: z.string(),
  title: z.string(),
  subtitle: z.string(),
  excerpt: z.string(),
  content: Content,
  author: z.string(),
  publishedDate: z.string(),
  readTime: z.string(),
  tags: z.array(z.string()),
  image: z.string(),
  category: z.string(),
  featured: z.boolean(),
  views: z.number(),
  likes: z.number(),
});

export const BlogsSchema = z.object({
  blogs: z.array(Blog),
});

