"use client";

import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Autoplay } from "swiper/modules";
import { Star, ChevronLeft, ChevronRight } from "lucide-react";
import { useRef } from "react";

const testimonials = [
  {
    name: "Jane D",
    role: "CEO",
    image: "https://pagedone.io/asset/uploads/1696229969.png",
    rating: 5,
    text: "The user interface of this platform is so intuitive, I was able to start using it without any guidance.",
  },
  {
    name: "Harsh P.",
    role: "Product Designer",
    image: "https://pagedone.io/asset/uploads/1696229994.png",
    rating: 5,
    text: "I used to dread writing blogs, but this platform has made the process so much simpler and stress-free.",
  },
  {
    name: "Sarah M.",
    role: "Content Writer",
    image: "https://pagedone.io/asset/uploads/1696229969.png",
    rating: 5,
    text: "Amazing platform for sharing ideas and connecting with readers. Highly recommended for all writers!",
  },
  {
    name: "Mike R.",
    role: "Tech Blogger",
    image: "https://pagedone.io/asset/uploads/1696229994.png",
    rating: 5,
    text: "The best blogging platform I've used. Clean interface, great features, and excellent community support.",
  },
];

export default function Testimonial() {
  const prevRef = useRef(null);
  const nextRef = useRef(null);

  return (
    <section className="py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center gap-y-8 lg:gap-y-0 flex-wrap md:flex-wrap lg:flex-nowrap lg:flex-row lg:justify-between lg:gap-x-8 max-w-sm sm:max-w-2xl lg:max-w-full mx-auto">
          {/* Left Content */}
          <div className="w-full lg:w-2/5">
            <span className="text-sm text-gray-500 font-medium mb-4 block">
              Testimonial
            </span>
            <h2 className="text-4xl font-bold text-gray-900 leading-[3.25rem] mb-8">
              23k+ Customers gave their{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-tr from-indigo-600 to-violet-600">
                Feedback
              </span>
            </h2>

            {/* Slider Controls */}
            <div className="flex items-center justify-center lg:justify-start gap-10">
              <button
                ref={prevRef}
                className="group flex justify-center items-center border border-solid border-indigo-600 w-12 h-12 transition-all duration-500 rounded-lg hover:bg-indigo-600"
                aria-label="Previous testimonial"
              >
                <ChevronLeft className="h-6 w-6 text-indigo-600 group-hover:text-white" />
              </button>
              <button
                ref={nextRef}
                className="group flex justify-center items-center border border-solid border-indigo-600 w-12 h-12 transition-all duration-500 rounded-lg hover:bg-indigo-600"
                aria-label="Next testimonial"
              >
                <ChevronRight className="h-6 w-6 text-indigo-600 group-hover:text-white" />
              </button>
            </div>
          </div>

          {/* Swiper */}
          <div className="w-full lg:w-3/5">
            <Swiper
              modules={[Navigation, Autoplay]}
              spaceBetween={28}
              slidesPerView={1}
              loop={true}
              autoplay={{
                delay: 3000,
                disableOnInteraction: false,
              }}
              navigation={{
                prevEl: prevRef.current,
                nextEl: nextRef.current,
              }}
              onBeforeInit={(swiper) => {
                swiper.params.navigation.prevEl = prevRef.current;
                swiper.params.navigation.nextEl = nextRef.current;
              }}
              breakpoints={{
                768: {
                  slidesPerView: 2,
                  spaceBetween: 28,
                },
                1024: {
                  slidesPerView: 2,
                  spaceBetween: 32,
                },
              }}
              className="testimonial-swiper"
            >
              {testimonials.map((testimonial, index) => (
                <SwiperSlide key={index}>
                  <div className="group bg-white border border-solid border-gray-300 rounded-2xl max-sm:max-w-sm max-sm:mx-auto p-6 transition-all duration-500 hover:border-indigo-600 h-full">
                    <div className="flex items-center gap-5 mb-5 sm:mb-9">
                      <img
                        className="rounded-full object-cover w-16 h-16"
                        src={testimonial.image}
                        alt={testimonial.name}
                      />
                      <div className="grid gap-1">
                        <h5 className="text-gray-900 font-medium transition-all duration-500">
                          {testimonial.name}
                        </h5>
                        <span className="text-sm leading-6 text-gray-500">
                          {testimonial.role}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center mb-5 sm:mb-9 gap-2 text-amber-500 transition-all duration-500">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-current" />
                      ))}
                    </div>
                    <p className="text-sm text-gray-500 leading-6 transition-all duration-500 min-h-24 group-hover:text-gray-800">
                      {testimonial.text}
                    </p>
                  </div>
                </SwiperSlide>
              ))}
            </Swiper>
          </div>
        </div>
      </div>
    </section>
  );
}
