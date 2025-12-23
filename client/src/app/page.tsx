import Link from "next/link";
import type { FightDetails } from "~/types/fights";
import { LatestPost } from "~/app/_components/post";
import { api, HydrateClient } from "~/trpc/server";
import { Fights } from "~/app/_components/fights";

export default async function Home() {
  const hello = await api.post.hello({ text: "from tRPC" });

  void api.post.getLatest.prefetch();
  const fights: FightDetails[] = await api.predictor.getFights();

  return (
    <HydrateClient>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-[#e5e7eb] to-[#1f2937] text-black">
        <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem]">
            UFC <span className="text-[#dc2626]">Fight</span> Predictor
          </h1>
          <h2 className="text-2xl font-bold">
            Predicted winner of the next UFC event
          </h2>
          <div>
            <Fights fights={fights} />
          </div>

          {/* <LatestPost /> */}
        </div>
      </main>
    </HydrateClient>
  );
}
