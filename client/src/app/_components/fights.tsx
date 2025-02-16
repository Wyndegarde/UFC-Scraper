"use client";


import type { FightsProps } from "~/types/fights";
import { FightDetails } from "~/app/_components/fightDetails";

export function Fights({ fights }: FightsProps) {
  return (
    <div>
      {fights.map((fight) => (
        <FightDetails fight={fight} key={fight.red_fighter} />
      ))}
    </div>
  );
}
