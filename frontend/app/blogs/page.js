"use client";

import { useState } from "react";
import BlogCard from "@/components/BlogCard";
import Breadcrumb from "@/components/Breadcrumb";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";

// Dummy blogs data (9 per page for pagination)
const allBlogs = [
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
  {
    slug: "healthy-eating-habits",
    title: "Building Healthy Eating Habits That Last",
    description: "Discover sustainable approaches to nutrition and develop eating habits that support your long-term health and wellness goals.",
    image: "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&h=400&fit=crop",
    category: "Lifestyle",
    date: "Jan 6, 2025",
  },
  {
    slug: "web-design-trends-2025",
    title: "Top Web Design Trends to Watch in 2025",
    description: "Stay ahead of the curve with these cutting-edge web design trends that are shaping the digital landscape this year.",
    image: "https://images.unsplash.com/photo-1558655146-364adaf1fcc9?w=800&h=400&fit=crop",
    category: "Technology",
    date: "Jan 4, 2025",
  },
  {
    slug: "budget-travel-europe",
    title: "How to Travel Europe on a Budget: The Complete Guide",
    description: "Explore Europe without breaking the bank. Money-saving tips, budget accommodation, and free attractions across the continent.",
    image: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=400&fit=crop",
    category: "Travel",
    date: "Jan 2, 2025",
  },
  {
    slug: "morning-routine-productivity",
    title: "The Perfect Morning Routine for Maximum Productivity",
    description: "Transform your mornings and boost your productivity with these science-backed morning routine strategies and habits.",
    image: "https://images.unsplash.com/photo-1495364141860-b0d03eccd065?w=800&h=400&fit=crop",
    category: "Lifestyle",
    date: "Dec 30, 2024",
  },
  {
    slug: "typescript-advanced-tips",
    title: "Advanced TypeScript Tips for Professional Developers",
    description: "Level up your TypeScript skills with advanced techniques, type utilities, and patterns used by professional developers.",
    image: "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&h=400&fit=crop",
    category: "Technology",
    date: "Dec 28, 2024",
  },
];

const categories = ["All", "Technology", "Travel", "Lifestyle"];
const BLOGS_PER_PAGE = 9;

export default function BlogsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);

  // Filter blogs
  const filteredBlogs = allBlogs.filter((blog) => {
    const matchesSearch =
      blog.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      blog.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === "All" || blog.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Pagination
  const totalPages = Math.ceil(filteredBlogs.length / BLOGS_PER_PAGE);
  const startIndex = (currentPage - 1) * BLOGS_PER_PAGE;
  const endIndex = startIndex + BLOGS_PER_PAGE;
  const currentBlogs = filteredBlogs.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setCurrentPage(1);
  };

  const breadcrumbItems = [
    { label: "Home", href: "/" },
    { label: "Blogs", href: null },
  ];

  return (
    <div className="py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <Breadcrumb items={breadcrumbItems} />

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Explore Our Blogs
          </h1>
          <p className="text-lg text-gray-600">
            Discover stories, thinking, and expertise from writers on any topic.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search blogs by title or content..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => handleCategoryChange(category)}
                className={`px-5 py-2 rounded-lg font-medium transition-colors ${
                  selectedCategory === category
                    ? "bg-indigo-600 text-white"
                    : "bg-white text-gray-700 border border-gray-300 hover:border-indigo-600 hover:text-indigo-600"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {currentBlogs.length} of {filteredBlogs.length} blog
            {filteredBlogs.length !== 1 ? "s" : ""}
          </p>
        </div>

        {/* Blog Grid */}
        {currentBlogs.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {currentBlogs.map((blog) => (
                <BlogCard key={blog.slug} blog={blog} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                  Previous
                </button>

                <div className="flex items-center gap-2">
                  {[...Array(totalPages)].map((_, index) => {
                    const page = index + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                          currentPage === page
                            ? "bg-indigo-600 text-white"
                            : "bg-white text-gray-700 border border-gray-300 hover:border-indigo-600 hover:text-indigo-600"
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() =>
                    setCurrentPage((prev) => Math.min(prev + 1, totalPages))
                  }
                  disabled={currentPage === totalPages}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-16">
            <p className="text-xl text-gray-600 mb-4">No blogs found</p>
            <p className="text-gray-500">
              Try adjusting your search or filter to find what you're looking for.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
