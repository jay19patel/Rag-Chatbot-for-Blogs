import Link from "next/link";
import { ArrowRight, BookOpen, Users, TrendingUp } from "lucide-react";
import BlogCard from "@/components/BlogCard";
import Testimonial from "@/components/Testimonial";
import FAQ from "@/components/FAQ";

// Dummy featured blogs data
const featuredBlogs = [
  {
    slug: "getting-started-with-nextjs",
    title: "Getting Started with Next.js 15: A Comprehensive Guide",
    description: "Learn how to build modern web applications with Next.js 15. Explore the latest features, routing, and best practices.",
    image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=400&fit=crop",
    category: "Technology",
    date: "Jan 15, 2025",
  },
  {
    slug: "travel-guide-to-japan",
    title: "The Ultimate Travel Guide to Japan in 2025",
    description: "Discover the best places to visit, authentic cuisine to try, and cultural experiences you shouldn't miss in Japan.",
    image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=400&fit=crop",
    category: "Travel",
    date: "Jan 12, 2025",
  },
  {
    slug: "minimalist-lifestyle-tips",
    title: "10 Simple Tips for Embracing a Minimalist Lifestyle",
    description: "Transform your life with minimalism. Learn practical tips to declutter your space and mind for a more peaceful living.",
    image: "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&h=400&fit=crop",
    category: "Lifestyle",
    date: "Jan 10, 2025",
  },
  {
    slug: "react-best-practices",
    title: "React Best Practices Every Developer Should Know",
    description: "Improve your React development skills with these essential best practices, patterns, and performance optimization techniques.",
    image: "https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?w=800&h=400&fit=crop",
    category: "Technology",
    date: "Jan 8, 2025",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="py-20 md:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6">
              Welcome to{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
                BlogHub
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 leading-relaxed">
              Create, share, and explore amazing blogs. Join our community of passionate writers and curious readers.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                href="/login"
                className="w-full sm:w-auto bg-indigo-600 text-white px-8 py-4 rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-lg flex items-center justify-center gap-2"
              >
                Login
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/register"
                className="w-full sm:w-auto bg-white text-gray-900 px-8 py-4 rounded-lg border-2 border-gray-300 hover:border-indigo-600 hover:text-indigo-600 transition-colors font-semibold text-lg"
              >
                Register
              </Link>
              <button className="w-full sm:w-auto bg-white text-gray-900 px-8 py-4 rounded-lg border-2 border-gray-300 hover:border-gray-400 transition-colors font-semibold text-lg flex items-center justify-center gap-2">
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Continue with Google
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-3xl mx-auto">
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-3">
                  <BookOpen className="w-8 h-8 text-indigo-600" />
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-1">10k+</h3>
                <p className="text-gray-600">Published Blogs</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-violet-100 rounded-full flex items-center justify-center mb-3">
                  <Users className="w-8 h-8 text-violet-600" />
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-1">50k+</h3>
                <p className="text-gray-600">Active Users</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mb-3">
                  <TrendingUp className="w-8 h-8 text-pink-600" />
                </div>
                <h3 className="text-3xl font-bold text-gray-900 mb-1">1M+</h3>
                <p className="text-gray-600">Monthly Reads</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Blogs Section */}
      <section className="py-16 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                Featured Blogs
              </h2>
              <p className="text-gray-600">
                Discover the latest stories from our community
              </p>
            </div>
            <Link
              href="/blogs"
              className="hidden sm:flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-semibold transition-colors"
            >
              View All
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredBlogs.map((blog) => (
              <BlogCard key={blog.slug} blog={blog} />
            ))}
          </div>

          <div className="mt-8 text-center sm:hidden">
            <Link
              href="/blogs"
              className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-semibold transition-colors"
            >
              View All Blogs
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <Testimonial />

      {/* FAQ Section */}
      <FAQ />

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-violet-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Start Your Blogging Journey?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join thousands of writers and readers in our growing community
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 bg-white text-indigo-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition-colors font-semibold text-lg"
          >
            Get Started for Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </>
  );
}
