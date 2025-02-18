"use client";

import type { FightsProps } from "~/types/fights";
import { FightDetails } from "~/app/_components/fightDetails";

export function Fights({ fights }: FightsProps) {
  return (
    <div className="max-w-6xl mx-auto overflow-x-auto rounded-lg shadow-lg bg-white/90">
      <table className="w-full border-collapse text-black">
        <thead className="bg-gray-100/90">
          <tr>
            <th className="px-6 py-4 text-left text-sm font-semibold border-b border-gray-200/70">
              Red Fighter
            </th>
            <th className="px-6 py-4 text-left text-sm font-semibold border-b border-gray-200/70">
              Blue Fighter
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200/50">
          {fights.map((fight) => (
            <FightDetails fight={fight} key={fight.red_fighter} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
