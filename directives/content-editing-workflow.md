# Content Editing Workflow

## Google Drive Folder IDs
| Folder | ID | Purpose |
|---|---|---|
| Longform | `1qShA0yM0y4wCjrg3FnyBcwdlJYrHDvG_` | Marco drops unedited long-form videos here |
| Shortform | `1PLwWssFiFCcbgMYvXWf0g-OetAdPrL_4` | Marco drops unedited short-form videos here |
| Finishedproducts | `1K00FFTtK5ojgDYGG33OXrbmpaMcQyNCt` | Upload all completed edits here |
| Cover | `12oJACBura3fYzMlnmM-poyx1vE5fwsgj` | Upload thumbnails/covers here |

## Workflow (every time)

1. **Marco uploads** raw video to `Longform/` or `Shortform/`
2. **I detect** the new file (Marco tells me, or I check on request)
3. **Edit the video** (or produce edit instructions/script for the content team)
4. **Upload finished edit** to `Finishedproducts/`
5. **Generate thumbnail** if applicable → upload to `Cover/`
6. **Delete the original** from `Longform/` or `Shortform/`

## Commands
```bash
# Check for new files in Longform
gog drive search "'1qShA0yM0y4wCjrg3FnyBcwdlJYrHDvG_' in parents" -a marcolevy54@gmail.com

# Check for new files in Shortform
gog drive search "'1PLwWssFiFCcbgMYvXWf0g-OetAdPrL_4' in parents" -a marcolevy54@gmail.com

# Upload to Finishedproducts
gog drive upload /path/to/file --parent 1K00FFTtK5ojgDYGG33OXrbmpaMcQyNCt -a marcolevy54@gmail.com

# Upload to Cover
gog drive upload /path/to/thumbnail --parent 12oJACBura3fYzMlnmM-poyx1vE5fwsgj -a marcolevy54@gmail.com

# Delete original
gog drive delete <FILE_ID> -a marcolevy54@gmail.com
```

## Notes
- longform-bot handles long-form video editing tasks
- shortform-bot handles short-form + carousel editing tasks
- Always confirm with Marco before deleting originals if there's any ambiguity
