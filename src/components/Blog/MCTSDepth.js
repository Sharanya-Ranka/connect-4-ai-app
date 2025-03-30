// src/components/MCTSDepth.js
import React from "react";
import {
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from "react-accessible-accordion";
import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css"; // Import KaTeX styles

function MCTSDepth({ content }) {
  return (
    <AccordionItem>
      <AccordionItemHeading>
        <AccordionItemButton>MCTS in depth</AccordionItemButton>
      </AccordionItemHeading>
      <AccordionItemPanel>
        For example, here is a formula: <InlineMath math="\sum_{i=1}^{n} i^2" />
      </AccordionItemPanel>
    </AccordionItem>
  );
}

export default MCTSDepth;
