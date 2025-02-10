import React from "react";
import { Timeline } from "@/components/ui/timeline";

export default function TimelineDemo() {
  const data = [
    {
      title: "March 21 – Expo & Workshop Day",
      content: (
        <div>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-8">
            A day of keynotes, discussions, and hands-on workshops to equip participants before the hackathon.
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             10:00 AM – Event Inauguration & Welcome Ceremony
            🎤 Official Opening | 👋 Welcome Address | 🏆 Felicitation of Guests
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             10:30 AM – Keynote Speech
            🎙 Insightful Talk by an Industry Expert | 🚀 Innovation & Future Tech
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             11:20 AM – Presentations by Community Partners
            🛠 Tech Showcases | 📊 Live Demos | 💡 API & Tool Introductions
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             12:20 PM – Interactive Panel Discussion
            💬 Expert Panel | 🔹 AI & ML Trends | 🔹 Future of Web3 | 🔹 Open-Source Impact
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
            🍽 1:00 PM – Lunch Break
            🥗 Networking & Refreshments
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             2:00 PM - 5:00 PM – Hands-On Workshop Sessions
            🔹 🤖 Gen AI | 🔹 🌐 Web3 | 🔹 💻 Web2 | 🔹 🆓 Open-Source
          </p>
        </div>
      ),
    },
    {
      title: "March 22 – Hackathon Begins (30-Hour Challenge)",
      content: (
        <div>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins  mb-8">
            🔥 The ultimate coding battle begins with 500+ participants, 30 hours, and endless possibilities!
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             9:30 AM – Welcome & Hackathon Challenge Announcement
            🎤 Kickoff Speech | 📢 Challenge Statements Revealed | ⚠ Guidelines & Rules
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             9:45 AM – Hackathon Officially Begins
            💻 Teams Assemble | 🛠 Coding & Prototyping Start
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
            ⏳ 12:00 PM – Mentorship & Guidance
            👨‍🏫 Expert Support | ✔ Debugging | ✔ AI Model Training | ✔ Cloud Deployment
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
            🍽 1:30 PM – Lunch Break
            🥪 Quick Refuel & Recharge
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             2:00 PM – Development Sprint Continues
            ⚙ Feature Implementation | 📍 Progress Checkpoints
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             7:00 PM – Networking & Fun Activities
            🎭 Tech Talks | Games | Relaxation
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-poppins mb-4">
             12:00 AM (Midnight) – Midnight Snacks & Coffee Break
            ☕ Late-Night Boost for Participants
          </p>
        </div>
      ),
    },
    {
      title: "March 23 – Hackathon Ends & Judging",
      content: (
        <div>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-8">
            🏆 The final stretch – project submissions, evaluations, and winners!
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             4:00 AM – Overnight Coding Sprint
            🔥 Finalizing Core Features | Debugging
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             8:00 AM – Morning Stand-Up & Last-Minute Tweaks
            ☕ Coffee Boost | 🚀 Final Adjustments
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             3:45 PM – Hackathon Submission Deadline
            📩 Final Project Upload | ✔ Code & Docs Ready
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             4:00 PM – Project Judging Begins
            ⚖ Evaluation Criteria: 🔹 💡 Innovation & Creativity | 🔹 ⚙ Technical Complexity | 🔹 🌍 Real-World Impact
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             6:00 PM – Winner Announcements & Prize Distribution
            🥇 Best Innovation | 🎨 Best UI/UX | 🌟 Most Impactful Solution
          </p>
          <p className="text-neutral-800 dark:text-neutral-200 text-sm md:text-lg font-roboto mb-4">
             6:30 PM – Closing Ceremony & Conclusion
            🎤 Final Remarks | 🎊 Networking & Celebration
          </p>
        </div>
      ),
    },
  ];
  
  return (
    <div className="w-full">
      <Timeline data={data} />
    </div>
  );
}
