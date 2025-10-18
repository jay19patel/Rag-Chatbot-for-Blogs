"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const faqItems = [
  {
    id: "1",
    title: "What makes BlogHub different from other platforms?",
    content:
      "BlogHub focuses on simplicity and user experience. Built with modern technologies, it offers excellent performance, follows accessibility standards, and provides a clean interface for both writers and readers. Our platform emphasizes community building and meaningful content.",
  },
  {
    id: "2",
    title: "How can I start writing blogs on BlogHub?",
    content:
      "Simply create a free account by clicking the 'Register' button. Once signed in, you'll have access to our intuitive blog editor where you can write, format, and publish your content. We support markdown, rich text editing, and image uploads.",
  },
  {
    id: "3",
    title: "Is BlogHub free to use?",
    content:
      "Yes! BlogHub offers a generous free tier that includes unlimited blog posts, image uploads, and access to our community features. We also offer premium plans with advanced analytics and customization options for professional writers.",
  },
  {
    id: "4",
    title: "How do I grow my audience on BlogHub?",
    content:
      "We provide built-in SEO optimization, social sharing features, and category-based discovery to help your content reach the right audience. Engage with other writers, use relevant tags, and maintain a consistent posting schedule. Our analytics dashboard helps you understand your readers better.",
  },
];

export default function FAQ() {
  const [openItem, setOpenItem] = useState("3");

  const toggleItem = (id) => {
    setOpenItem(openItem === id ? null : id);
  };

  return (
    <section className="py-24 bg-white/50">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <span className="text-sm text-gray-500 font-medium mb-4 block">
            FAQ
          </span>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-gray-600">
            Everything you need to know about BlogHub
          </p>
        </div>

        {/* Accordion */}
        <div className="space-y-3">
          {faqItems.map((item) => (
            <div
              key={item.id}
              className={`rounded-lg border bg-white px-6 py-1 transition-all duration-200 ${
                openItem === item.id
                  ? "border-indigo-600 ring-2 ring-indigo-600/20"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              {/* Trigger */}
              <button
                onClick={() => toggleItem(item.id)}
                className="flex w-full items-center justify-between py-4 text-left focus:outline-none"
              >
                <span className="text-[15px] leading-6 font-semibold text-gray-900">
                  {item.title}
                </span>
                <ChevronDown
                  className={`w-5 h-5 text-gray-500 transition-transform duration-200 flex-shrink-0 ml-4 ${
                    openItem === item.id ? "rotate-180" : ""
                  }`}
                />
              </button>

              {/* Content */}
              <div
                className={`overflow-hidden transition-all duration-200 ${
                  openItem === item.id ? "max-h-96 pb-4" : "max-h-0"
                }`}
              >
                <p className="text-gray-600 leading-relaxed">{item.content}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center p-8 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-xl border border-indigo-100">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Still have questions?
          </h3>
          <p className="text-gray-600 mb-4">
            Can't find the answer you're looking for? Please chat with our friendly team.
          </p>
          <a
            href="mailto:support@bloghub.com"
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
          >
            Contact Support
          </a>
        </div>
      </div>
    </section>
  );
}
