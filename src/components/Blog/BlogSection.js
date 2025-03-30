import React from "react";
import {
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from "react-accessible-accordion";
import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css"; // Import KaTeX styles
import "../../styles/Blog/BlogSection.css";

function BlogSection({ title, content }) {
  return (
    <AccordionItem>
      <AccordionItemHeading>
        <AccordionItemButton>{title}</AccordionItemButton>
      </AccordionItemHeading>
      <AccordionItemPanel>{content}</AccordionItemPanel>
    </AccordionItem>
  );
}

export default BlogSection;
