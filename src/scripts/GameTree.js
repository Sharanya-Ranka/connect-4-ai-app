class Tree {
  constructor(node_data, parents_data, root_key) {
    // Requires 3 parameters:
    // 1) node data (array of {key:, value:})
    // 2) parents_data (array of 2-length arrays [[child_key, parent_key], ...])
    // 3) root_key
    this.nodes = new Map(
      node_data.map((data) => [
        data.key,
        {
          key: data.key,
          value: data.value,
          children: [],
          parent: null,
        },
      ]),
    );

    parents_data.forEach((element) => {
      const parent = this.getNode(element[1]);
      const child = this.getNode(element[0]);

      parent.children.push(child.key);
      child.parent = parent.key;
    });

    this.root_key = root_key;
  }

  bfsTraverse() {
    const queue = [this.getNode(this.root_key)];
    while (queue.length > 0) {
      const node = queue.shift();
      //   console.log(node);
      node.children.forEach((element) => {
        queue.push(this.getNode(element));
      });
    }
  }
  printTreeNodes() {
    // console.log(this.nodes);
    return JSON.stringify(Array.from(this.nodes.entries()));
  }

  getNode(key) {
    return this.nodes.get(key);
  }
}

function getGameTreeData(height, children_per_node) {
  const nodes = Array.from({
    length: Math.pow(children_per_node, height + 1) - 1,
  }).map((el, ind) => ({ key: ind, value: ind }));

  const parents = nodes
    .filter((choice) => choice.key != 0)
    .map((node) => [node.key, parseInt((node.key - 1) / children_per_node)]);

  return { node_data: nodes, parents_data: parents, root_key: 0 };
}

export { Tree, getGameTreeData };

// functio
// const tree = new Tree();
// tree.constructFromData(
//   [
//     { key: 1, value: 1 },
//     { key: 2, value: 2 },
//     { key: 3, value: 3 },
//   ],
//   [
//     [3, 1],
//     [2, 1],
//   ],
//   1,
// );
// tree.printTreeNodes();
// tree.bfsTraverse();

// tree.greet();
