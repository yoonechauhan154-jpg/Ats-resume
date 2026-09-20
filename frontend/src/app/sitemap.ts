import type { MetadataRoute } from "next";

const BASE_URL = "https://ats-resumecheck.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE_URL}/`,
      changeFrequency: "monthly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/tool`,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/methodology`,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/faq`,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/guides`,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/guides/what-is-ats-resume-checker`,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/guides/ats-resume-myths`,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/guides/ats-resume-format-guide`,
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];
}