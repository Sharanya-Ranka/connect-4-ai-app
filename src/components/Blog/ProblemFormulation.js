// src/components/ProblemFormulation.js
import React from "react";
import {
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from "react-accessible-accordion";
import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css"; // Import KaTeX styles

function ProblemFormulation({ content }) {
  return (
    <AccordionItem>
      <AccordionItemHeading>
        <AccordionItemButton>Problem Formulation</AccordionItemButton>
      </AccordionItemHeading>
      <AccordionItemPanel>
        <BlockMath math="E = mc^2" />
      </AccordionItemPanel>
    </AccordionItem>
  );
}

export default ProblemFormulation;
