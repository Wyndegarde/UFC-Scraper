"use client";


import type { FightsProps } from "~/types/fights";
import { FightDetails } from "~/app/_components/fightDetails";

export function Fights({ fights }: FightsProps) {
  return (
    <div className="max-w-4xl mx-auto overflow-x-auto rounded-lg shadow-lg">
      <table className="w-full border-collapse bg-white/10 text-white">
        <thead className="bg-white/5">
          <tr>
            <th className="px-6 py-4 text-left text-sm font-semibold border-b border-white/10">
              Red Fighter
            </th>
            <th className="px-6 py-4 text-left text-sm font-semibold border-b border-white/10">
              Blue Fighter
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {fights.map((fight) => (
            <FightDetails fight={fight} key={fight.red_fighter} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
