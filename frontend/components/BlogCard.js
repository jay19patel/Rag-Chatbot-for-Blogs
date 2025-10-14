import Link from "next/link";
import { Calendar, Tag } from "lucide-react";

export default function BlogCard({ blog }) {
  return (
    <Link href={`/blogs/${blog.slug}`}>
      <div className="group bg-white rounded-xl border border-gray-200 overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-indigo-200">
        {/* Image */}
        <div className="relative h-48 overflow-hidden bg-gray-100">
          <img
            src={blog.image}
            alt={blog.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div className="absolute top-4 left-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white text-indigo-600 shadow-sm">
              {blog.category}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-indigo-600 transition-colors">
            {blog.title}
          </h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {blog.description}
          </p>

          {/* Meta */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>{blog.date}</span>
            </div>
            <div className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              <span>{blog.category}</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
