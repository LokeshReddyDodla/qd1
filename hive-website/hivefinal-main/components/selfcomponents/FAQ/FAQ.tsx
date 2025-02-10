"use client"
import React from 'react';
import { HyperText } from "@/components/ui/hyper-text";
import { Plus, Minus } from 'lucide-react';

const FAQ = () => {
  const [openIndex, setOpenIndex] = React.useState<number | null>(null);
 
const faqs = [
  {
    question: "Will there be food or refreshments?",
    answer: "Yes, we will be providing food and refreshments for all attendants, more information to come!"
  },
  {
    question: "Who can attend?",
    answer: "Anyone who is attending a university! Hackers must be 18+ years old and must be attending a college or university to participate."
  },
  {
    question: "Is there accommodation?",
    answer: "Yes, accommodation is available for participants; however, it must be arranged separately. Participants are responsible for booking and paying for their accommodation. Please note that the cost of accommodation is not included in the hackathon registration fee, and participants must cover these expenses on their own. We encourage you to make arrangements early to ensure availability during the event."
  },
  {
    question: "How big can teams be?",
    answer: "A team must comprise a minimum of 2 members and can include upto a maximum of 5 members."
  },
  {
    question: "What if I still have questions?",
    answer: "No worries, please e-mail us at hive@mlritm.ac.in and we will be more than happy to answer your question!"
  }
  
];


  return (
    <section id="faq" className="relative py-24 bg-black overflow-hidden">
      <div className="stars-1"></div>
      <div className="stars-2"></div>
      <div className="stars-3"></div>
      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="font-poppins text-4xl font-extrabold text-white sm:text-5xl">
            <HyperText>{`FAQ's`}</HyperText>
          </h2>
        </div>
        <div className="space-y-4 mt-6">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white/10 border border-white/20 backdrop-blur-lg shadow-lg rounded-2xl overflow-hidden"
            >
              <button
                className="w-full px-6 py-4 flex items-center justify-between text-left"
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
              >
                <span className="text-lg font-poppins text-white">{faq.question}</span>
                {openIndex === index ? (
                  <Minus className="w-5 h-5 text-white/80" />
                ) : (
                  <Plus className="w-5 h-5 text-white/80" />
                )}
              </button>
              {openIndex === index && (
                <div className="px-6 pb-4">
                  <p className="text-white/80 font-sans">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FAQ;