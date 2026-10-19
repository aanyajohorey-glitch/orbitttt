# data folder

ORBIT's datasets live here.

- `worlds.csv`: the sample aesthetic worlds. Each row is one world with
  its mood, description, the emotions it matches (GoEmotions labels such
  as `joy` or `nervousness`, used to recommend a world), colour palette,
  planet colours, visual elements,
  typography, sound vibe and one creative prompt for each intent
  (Explore, Digital Art, Poster, Presentation, Scrapbook). Columns that
  hold several values use `|` between them.

The emotion model itself is pre-trained and is not stored here. If you
later train your own comparison model, its dataset (for example
`moods.csv`) can also go in this folder.
