## Instructions on how to use the Circos Viz

### Selecting your texts 

Use the 'Select book 1' drop down to select a text that you would like to compare with other texts in the corpus. 'Select book 2' will then give a list of books that have text reuse with book 1. You can choose to sort these by 'reuse instances' (high to low) or 'death date' (low to high).

Use the sliders below each of the book selectors to give a range for the death dates of authors. 

Selecting books in either of these drop downs will populate the 'Current text selection' field. You can simply select texts from the 'Current text selection' field if you wish.

You can type in any drop down to filter the selection.

### Setting your Circos Options

In the 'Circos Options' tab you can set up how you would like to view your texts. 
You will need to set a main text - this is the core text you would like to compare. Relationships with that text will be given in a different colour and you will be able to see additional data on books related to this text through histograms.

'Show Reuse for all texts' will draw lines between all of the other texts (using purple as the colour for these lines).

You can choose to show statistics in the form of histograms on the outside of the Circos diagram. These histograms provide data for the main text. You can choose to either show the percentage word match with the main text, or the numbers of words matched with the main text.

When you're ready click 'Regenerate Circos Graph' to build the diagram. You will need to click this everytime you change your options or text selection (this helps to reduce the data demands of the application).

### *A note on loading times*

*If you select texts with lots of reuse, or a large number of texts, the diagram will take longer to build the diagram. Similarly, adding histograms or showing reuse for all of the texts will all increase load times. Be patient, the diagram will load (**if it does not, please submit a bug report**).*

### Using the diagram

The diagram uses passim aggregated data to show where reuse instances are located within a text, and where they are reused in compared texts. 

Each slice of the outer band represents a whole text, with zero being the start of the text. 

Each line represents a reuse instance between two texts. The thickness of the line corresponds to the size of the reuse instance (thinner and harder to distinguish lines correspond to shorter instances). Purple is used for all reuse instances and the colour of the main text used for main instances.

Hovering on a line will give the two book pairs and the location of the text reuse (in characters) - this will be updated to milestones in a later version.

To read reuse instances, click on the line (unfortunately this can be quite difficult for thin lines). Your selection will appear in the 'Alignment data' tab.

You can zoom into the diagram using the scroll on your mouse. This will help make thin lines more distinct. 



