from utils import *
from graphs import *

def final_page(name_db: str, section: str):
    st.write('Final page')

    # need to get the data for each restaurant
    data = Database_Manager(name_db).get_main_db_from_venue()
    with st.expander('View all data'):
        st.write(data)

    # get unique venues
    list_of_venue = data['Reservation: Venue'].unique()
    # for each venue get the ones with negative feedback
    for i, venue in enumerate(list_of_venue):
        venue_data = data[data['Reservation: Venue'] == venue]
        venue_data_to_lab = venue_data[venue_data['Sentiment'] == 'NEGATIVE']
        tot_ = len(venue_data_to_lab)
        tot_done = len(venue_data_to_lab[venue_data_to_lab['Label: Dishoom'] != ''])
        tot_not_done = len(venue_data_to_lab[venue_data_to_lab['Label: Dishoom'] == ''])

        # get total thumbs up and thumbs down
        # thumbs up emoji is  👍
        # thumbs down emoji is 👎
        thumbs_up = venue_data[venue_data['👍'] == '1']
        thumbs_down = venue_data[venue_data['👎'] == '1']

        # get suggestions 
        suggestions = venue_data[venue_data['💡'] == '1']

        
        with st.expander(venue + f' - {tot_done}/{tot_} ({round(tot_done/tot_*100, 2)}%)'):
          
            # now create a pie chart
            fig = go.Figure(data=[go.Pie(labels=['Done', 'Not Done'], values=[tot_done, tot_not_done])])
            fig.update_layout(title_text=f'{venue} - {tot_done}/{tot_} ({round(tot_done/tot_*100, 2)}%)')
            # green for done, red for not done
            fig.update_traces(marker_colors=['green', 'red'])
            # set opacity
            fig.update_traces(opacity=0.6, textinfo='percent+label')
            # set size 200x200
            fig.update_layout(width=300, height=300)
            st.plotly_chart(fig)


            c1,c2 = st.columns(2)
            with c1:
                st.write(f'👍 {len(thumbs_up)} / 3')
                for good in thumbs_up['Details'].tolist():
                    st.write(good)
                    st.write('---')

            with c2:
                st.write(f'👎 {len(thumbs_down)} / 3')
                for bad in thumbs_down['Details'].tolist():
                    st.write(bad)
                    st.write('---')
            st.write('---') 

            st.write(f'💡 {len(suggestions)}')
            for sugg in suggestions['Details'].tolist():
                st.write(sugg)
                st.write('---')

    # add a complete df 
    with st.expander('View all data'):
        st.write(data)

    # create a download link
    def get_table_download_link(data):
        # rename the columns that have emoji
        data = data.rename(columns={'👍': 'thumbs_up', '👎': 'thumbs_down', '💡': 'suggestions'})
        # create a link to download the dataframe
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download csv file</a>'
        return href


    st.markdown(get_table_download_link(data), unsafe_allow_html=True)




