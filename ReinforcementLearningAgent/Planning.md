# Connect4AI Reinforcement Learning Agent Planning

## Todo Today
- getMCTSEmpiricalActionProbabilties returns only actions. What about state values?
- getMCTSEmpiricalActionProbabilties action_bias conversion to uct scores for states.
- _MCTSSelection UCT scoring function check
- Do you need all steps when you have a NN bias provided? Do you need to perform 'random' playouts?

## Todo List

| Task                                   | Due Date    | Status     |
|-----------------------------------------|-------------|------------|
|Paper Reading| 2025-06-23 (Monday)|Ongoing|
|Investigate Environment Creation| 2025-06-23 (Monday)|Ongoing|

### Task Description and Comments
Paper Reading - Re-Read AlphaGo, AlphaGo Zero, and read AlphaZero too. Understand it from an implementation perspective, since you'll be implementing it

Investigate Environment Creation - You need a Python implementation of Connect4. Check if you can use an LLM to build this, or use your previous implementation itself. Compare the two!



---

## Project Phases

### 1. Paper Reading & Plan detailing

### 2. Python environment creation
Create the game implementation again. Prefer "immutable" lean states this time. Refer to your previous implementation for logic.

### 3. AlphaZero based Implementation
Try a vanilla implementation first, the way you understand it. Then refer to the paper to see how you can improve it.
Perhaps talk to Danish?
#### 3.1. Design the Neural Network
- Input: Board state (nxm matrix)
- Output: Action probabilities
- Loss: Cross entropy loss for action probabilities, MSE for value function
- Architecture: Convolutional layers followed by fully connected layers
#### 3.2. MCTS Add-On
- Implement Monte Carlo Tree Search (MCTS) to sample actions based on the neural network's output

#### 3.3. Self-Play
- Implement self-play to generate training data
- MCTS will provide the "refined" action probabilities
- Game outcome will provide the value function. Should this be all states from start to terminal/penultimate state, or just the terminal state?
- Save all information in the agent

#### 3.4. Training Loop
- Train the neural network using the data generated from self-play (few epochs)

#### 3.5. Considerations
- Can you utilize one Neural Network for all board sizes? Using a static 10 by 10 grid, with an additional input type to represent "cell does not exist" to represent smaller boards?"


### 4. Embedding into App
- Check if there are any Javascript ML frameworks to transfer the weights and use them client-side. I think Tensorflow has something like this.


### 5. Update Blog-documentation
- Finish the original blog post (MCTS only)
- Then move on to the AlphaZero enhancement.

---

## Comments
- Understand various Deep Reinforcement Learning terms (PPO, DPO, AlphaZero, DQNs). How do they relate to one another if they're all using Deep Neural Nets, and are all inputting state and outputting Action probabilities or Q values ?
