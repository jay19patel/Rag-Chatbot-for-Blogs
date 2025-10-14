import Link from "next/link";
import { Calendar, Tag, Clock, ArrowLeft, Share2 } from "lucide-react";
import Breadcrumb from "@/components/Breadcrumb";

// Dummy blog data (in real app, this would come from API/database)
const blogData = {
  title: "Getting Started with Next.js 15: A Comprehensive Guide",
  description: "Learn how to build modern web applications with Next.js 15.",
  image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=1200&h=600&fit=crop",
  category: "Technology",
  date: "January 15, 2025",
  readTime: "8 min read",
  author: {
    name: "John Doe",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop",
    role: "Senior Developer",
  },
  content: `
    <p>Next.js 15 brings a host of exciting new features and improvements that make building modern web applications easier and more efficient than ever before. In this comprehensive guide, we'll explore the key features and best practices for working with Next.js 15.</p>

    <h2>What's New in Next.js 15?</h2>
    <p>The latest version of Next.js introduces several groundbreaking features that enhance both developer experience and application performance. From improved routing capabilities to enhanced image optimization, Next.js 15 sets a new standard for React-based frameworks.</p>

    <h3>Enhanced App Router</h3>
    <p>The App Router in Next.js 15 has been significantly improved, offering better performance and more intuitive APIs. Developers can now create complex routing structures with ease, leveraging powerful features like nested layouts and loading states.</p>

    <h3>Server Components by Default</h3>
    <p>Server Components are now the default in Next.js 15, providing automatic code splitting and reduced JavaScript bundle sizes. This architectural shift enables faster page loads and improved SEO performance out of the box.</p>

    <h2>Getting Started</h2>
    <p>To begin working with Next.js 15, you'll need Node.js 18.17 or later installed on your system. Creating a new Next.js project is straightforward with the create-next-app CLI tool.</p>

    <h3>Installation</h3>
    <p>Run the following command to create a new Next.js 15 application:</p>
    <pre>npx create-next-app@latest my-app</pre>

    <h2>Best Practices</h2>
    <p>When working with Next.js 15, following best practices ensures optimal performance and maintainability. Here are some key recommendations:</p>

    <ul>
      <li>Leverage Server Components for data fetching</li>
      <li>Use the built-in Image component for automatic optimization</li>
      <li>Implement proper error boundaries for graceful error handling</li>
      <li>Utilize dynamic imports for code splitting</li>
      <li>Follow the recommended file structure and naming conventions</li>
    </ul>

    <h2>Conclusion</h2>
    <p>Next.js 15 represents a significant leap forward in web development frameworks. By embracing its new features and following best practices, developers can build fast, scalable, and maintainable applications that deliver exceptional user experiences.</p>
  `,
};

export default function BlogPostPage({ params }) {
  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Blogs", href: "/blogs" },
    { label: blogData.title, href: null },
  ];

  return (
    <div className="py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <Breadcrumb items={breadcrumbItems} />

        {/* Back Button */}
        <Link
          href="/blogs"
          className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Blogs
        </Link>

        {/* Blog Header */}
        <article className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-8">
          {/* Banner Image */}
          <div className="relative h-96 bg-gray-100">
            <img
              src={blogData.image}
              alt={blogData.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Content */}
          <div className="p-8 md:p-12">
            {/* Category Badge */}
            <div className="mb-4">
              <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-600">
                {blogData.category}
              </span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              {blogData.title}
            </h1>

            {/* Meta Information */}
            <div className="flex flex-wrap items-center gap-6 text-gray-600 mb-8 pb-8 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                <span>{blogData.date}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                <span>{blogData.readTime}</span>
              </div>
              <div className="flex items-center gap-2">
                <Tag className="w-5 h-5" />
                <span>{blogData.category}</span>
              </div>
            </div>

            {/* Author Info */}
            <div className="flex items-center justify-between mb-8 pb-8 border-b border-gray-200">
              <div className="flex items-center gap-4">
                <img
                  src={blogData.author.avatar}
                  alt={blogData.author.name}
                  className="w-12 h-12 rounded-full object-cover"
                />
                <div>
                  <p className="font-semibold text-gray-900">
                    {blogData.author.name}
                  </p>
                  <p className="text-sm text-gray-600">{blogData.author.role}</p>
                </div>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:border-indigo-600 hover:text-indigo-600 transition-colors">
                <Share2 className="w-5 h-5" />
                Share
              </button>
            </div>

            {/* Blog Content */}
            <div
              className="prose prose-lg max-w-none prose-headings:font-bold prose-h2:text-3xl prose-h2:mt-12 prose-h2:mb-4 prose-h3:text-2xl prose-h3:mt-8 prose-h3:mb-3 prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-6 prose-ul:my-6 prose-li:text-gray-700 prose-li:mb-2 prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:p-4 prose-pre:rounded-lg"
              dangerouslySetInnerHTML={{ __html: blogData.content }}
            />
          </div>
        </article>

        {/* Back Button Bottom */}
        <div className="text-center">
          <Link
            href="/blogs"
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to All Blogs
          </Link>
        </div>
      </div>
    </div>
  );
}

// Generate static params for all blog posts
export async function generateStaticParams() {
  // In a real app, you would fetch all blog slugs from your API/database
  return [
    { slug: "getting-started-with-nextjs" },
    { slug: "travel-guide-to-japan" },
    { slug: "minimalist-lifestyle-tips" },
    { slug: "react-best-practices" },
    { slug: "healthy-eating-habits" },
    { slug: "web-design-trends-2025" },
    { slug: "budget-travel-europe" },
    { slug: "morning-routine-productivity" },
    { slug: "typescript-advanced-tips" },
  ];
}
