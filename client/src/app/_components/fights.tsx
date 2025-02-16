"use client";


import type { FightsProps } from "~/types/fights";
import { FightDetails } from "~/app/_components/fightDetails";

export function Fights({ fights }: FightsProps) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className="text-left">Red Fighter</th>
          <th className="text-left">Blue Fighter</th>
        </tr>
      </thead>
      <tbody>
        {fights.map((fight) => (
          <FightDetails fight={fight} key={fight.red_fighter} />
        ))}
      </tbody>
    </table>
  );
}
