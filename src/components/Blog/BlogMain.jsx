// src/components/Blog.js
import React from "react";
import {
  Accordion,
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from "react-accessible-accordion";
import "react-accessible-accordion/dist/fancy-example.css";

import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css"; // Import KaTeX styles

import blogContent from "../../data/blogContent1.json";
import BlogSection from "./BlogSection";
import BlogQuickSummary from "./BlogQuickSummary.mdx"
import BlogMonteCarloTreeSearch from "./BlogMonteCarloTreeSearch.mdx"
import BlogUpperConfidenceBound from "./BlogUpperConfidenceBound.mdx"

function Blog() {
  const [contentData, setContentData] = React.useState([]);

  // console.log(blogContent);

  React.useEffect(() => {
    setContentData(blogContent);
  }, []);

  const renderContent = (contentArray) => {
    console.log("Content array=", contentArray);
    return contentArray.map((item) => {
      if (item.type === "paragraph") {
        return <p>{item.value}</p>;
      } else if (item.type === "latex") {
        return <BlockMath math={item.value} />;
      } else {
        return null; // Handle unknown types
      }
    });
  };
  const sectionData = [
  { title: "Quick Summary", content: <BlogQuickSummary /> },
  // { title: "Monte Carlo Tree Search", content: <BlogMonteCarloTreeSearch /> },
  // { title: "Upper Confidence Bound for Trees", content: <BlogUpperConfidenceBound /> },
];

  const accordionItems = sectionData.map((section, index) => (
    <BlogSection uuid={index} title={section.title} content={section.content} />
  ));
  // Object.entries(blogContent).map(([key, value]) => {
  //   // Perform your operation here with key and value
  //   return (<AccordionItem>
  //     <BlogSection title={value.title} content={renderContent(value.data)} />
  //   </AccordionItem>); // Example: creating an array of strings
  // });

  return (
    <div className="blog">
      {/* <h1>Understanding Monte Carlo Tree Search</h1>
      <h1>Coming Soon!</h1> */}

      <Accordion allowZeroExpanded allowMultipleExpanded={true} preExpanded={[0]}>
        {accordionItems}
        {/* <AccordionItem>
          <BlogSection
            title={blogContent.BlogGist.title}
            content={renderContent(blogContent.BlogGist.data)}
          />
        </AccordionItem>
        <AccordionItem>
          <BlogSection
            title={blogContent.ProblemFormulation.title}
            content={renderContent(blogContent.ProblemFormulation.data)}
          />
        </AccordionItem>
        <AccordionItem>
          <BlogSection
            title={blogContent.MCTSDepth.title}
            content={renderContent(blogContent.MCTSDepth.data)}
          />
        </AccordionItem> */}
      </Accordion>
    </div>
  );
}

export default Blog;

{
  /* <Accordion preExpanded={['a', 'c']}>
  <AccordionItem uuid="a" /> // Will be expanded by default
  <AccordionItem uuid="b" />
  <AccordionItem uuid="c" /> // Will be expanded by default
  <AccordionItem uuid="d" />
</Accordion> */
}

{
  /* <Accordion allowZeroExpanded>
    {items.map((item) => (
        <AccordionItem key={item.uuid}>
            <AccordionItemHeading>
                <AccordionItemButton>
                    {item.heading}
                </AccordionItemButton>
            </AccordionItemHeading>
            <AccordionItemPanel>
              {item.content}
            </AccordionItemPanel>
        </AccordionItem>
    ))}
</Accordion> */
}

{
  /* <Accordion allowMultipleExpanded={false}>
    {items.map((item) => (
        <AccordionItem key={item.uuid}>
            <AccordionItemHeading>
                <AccordionItemButton>
                    {item.heading}
                </AccordionItemButton>
            </AccordionItemHeading>
            <AccordionItemPanel>
              {item.content}
            </AccordionItemPanel>
        </AccordionItem>
    ))}
</Accordion> */
}
