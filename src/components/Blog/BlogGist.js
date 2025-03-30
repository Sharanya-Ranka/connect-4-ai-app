import React from "react";
import {
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from "react-accessible-accordion";
import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css"; // Import KaTeX styles

function BlogGist({ content }) {
  return (
    <AccordionItem>
      <AccordionItemHeading>
        <AccordionItemButton>The Gist</AccordionItemButton>
      </AccordionItemHeading>
      <AccordionItemPanel>
        So, you've seen AI making these 'genius' moves, huh? Feeling like it's
        some kind of digital sorcery? Let's break the illusion. At its heart,
        something like Monte Carlo Tree Search (MCTS) with UCT is basically
        just... playing a ridiculous number of games. Think of it like this:
        every time you make a move, the AI is like, 'Hold on, let me try a
        thousand different ways to finish this game real quick.' It's not
        exactly reading your mind; it's just really, really fast at playing
        pretend. One of the oldest tricks in the computer science playbook is
        turning 'how do I build an answer?' problems into 'let's just try
        everything and see what works!' problems. It's like, instead of
        carefully crafting a masterpiece, you just throw paint at the canvas
        until something kinda looks like a masterpiece. MCTS is just a fancy way
        of throwing paint, but it's got a few little tricks to make sure it's
        not just random splatters. Those 'tricks' are the heuristics, they are
        how we tell the AI 'try looking in these areas first, they are more
        likely to be good'. Think of it like a chef who can't cook but has a
        thousand interns. Each intern tries a slightly different recipe, and the
        chef just picks the one that doesnt make people vomit. That's MCTS for
        you: a lot of guesswork, a dash of efficiency, and a whole lot of 'let's
        see what happens!
      </AccordionItemPanel>
    </AccordionItem>
  );
}

export default BlogGist;
