import ast

  # Open Dalle prefixes

  
with open('pre_dalle.txt', 'r') as file:
    pre_dalle = file.read()
            
dalle_prefixes = ast.literal_eval(pre_dalle)

print(dalle_prefixes)

seed_val = 18197194

 # Use self.seed_val to choose a prefix
seed_val = str(seed_val)
seed_sum = 0
for dig in seed_val:
    seed_sum += int(dig)
print(seed_sum)

# Use seed sum to choose a prefix

prefix_index = seed_sum % len(dalle_prefixes)
selected_prefix = dalle_prefixes[prefix_index]

print(selected_prefix)
                
