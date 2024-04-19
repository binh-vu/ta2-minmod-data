import argparse
import pandas as pd
import networkx as nx
from sparql_generate_query import run_minmod_query

# -------- main --------------


def main(args):
    commodity = args.commodity
    output_directory = args.output_directory

    query = ''' SELECT ?ms1 ?ms2
                WHERE {
                    ?ms1 a :MineralSite .
                    ?ms2 a :MineralSite .
    
                    ?ms1 owl:sameAs ?ms2 .
                } '''
    df_all_sites = run_minmod_query(query, values=True)
    G = nx.from_pandas_edgelist(df_all_sites, source='ms1.value', target='ms2.value')

    # Find connected components
    groups = nx.connected_components(G)

    # Create a mapping from value to group ID
    group_mapping = {}
    for group_id, group in enumerate(groups, start=1):
        for value in group:
            group_mapping[value] = group_id

    # Map group IDs to the dataframe
    df_all_sites['group_id'] = df_all_sites['ms1.value'].map(group_mapping)

    # ------------------ Mineral Site to Grade-Tonnage data  ------------------

    # get aggregated (and transformed) grade-tonnage data for Mineral Sites
    query = '''
    SELECT 
      ?ms                                              # Mineral Site URI
      ?ms_name                                         # Mineral Site Name
      ?country                                         # Country
      ?loc_wkt                                         # WKT Geometry
      ?state_or_province
      ?total_tonnage_measured
      ?total_tonnage_indicated
      ?total_tonnage_inferred
      ?total_contained_measured
      ?total_contained_indicated
      ?total_contained_inferred
      (?total_tonnage_measured + ?total_tonnage_indicated + ?total_tonnage_inferred AS ?total_tonnage)                     # Total Tonnage [million tonnes]
      (?total_contained_measured + ?total_contained_indicated + ?total_contained_inferred AS ?total_contained_metal)
      (IF(?total_tonnage > 0, ?total_contained_metal / ?total_tonnage, 0) AS ?total_grade)                                 # Total Grade
    WHERE {
      {
        SELECT ?ms ?ms_name ?country ?loc_wkt ?state_or_province
               (SUM(?tonnage_measured) AS ?total_tonnage_measured)
               (SUM(?tonnage_indicated) AS ?total_tonnage_indicated)
               (SUM(?tonnage_inferred) AS ?total_tonnage_inferred)
               (SUM(?contained_measured) AS ?total_contained_measured)
               (SUM(?contained_indicated) AS ?total_contained_indicated)
               (SUM(?contained_inferred) AS ?total_contained_inferred)
        WHERE {

            ?ms :mineral_inventory ?mi .
            OPTIONAL { ?ms rdfs:label|:name ?ms_name . FILTER (STR(?ms_name) != "") }

            OPTIONAL { ?ms :location_info ?loc .
            
            OPTIONAL { ?loc :country ?country . FILTER (STR(?country) != "") }
            OPTIONAL { ?loc :state_or_province ?state_or_province . FILTER (STR(?state_or_province) != "") }
            OPTIONAL { ?loc :location ?loc_wkt . FILTER (STR(?loc_wkt) != "") }
            
            }
            

            ?mi :category ?mi_cat .
            ?mi :commodity [ :name ?name ] .
            FILTER(LCASE(STR(?name)) = "%s")

            {
                SELECT ?mi (MAX(?ore_val) AS ?max_ore_val) (SAMPLE(?grade_val) AS ?matched_grade_val)
                WHERE {
                    ?mi :ore [ :ore_value ?ore_val_raw; :ore_unit ?ore_unit] .
                    OPTIONAL { ?mi :grade [ :grade_value ?grade_val; :grade_unit ?grade_unit] . }
                    BIND(IF(bound(?ore_val_raw), ?ore_val_raw, 0) AS ?ore_val_pre)
                    BIND(IF(?ore_unit = <https://minmod.isi.edu/resource/Q202>, ?ore_val_pre, IF(?ore_unit = <https://minmod.isi.edu/resource/Q200>, ?ore_val_pre / 1e6, ?ore_val_pre)) AS ?ore_val)
                }
                GROUP BY ?mi
            }

            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "measured"), ?max_ore_val, 0) AS ?tonnage_measured)
            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "indicated"), ?max_ore_val, 0) AS ?tonnage_indicated)
            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "inferred"), ?max_ore_val, 0) AS ?tonnage_inferred)

            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "measured") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_measured)
            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "indicated") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_indicated)
            BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "inferred") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_inferred)

        }
        GROUP BY ?ms ?ms_name ?country ?loc_wkt ?state_or_province
      }
    }
    ''' % (commodity)
    query_resp_df = run_minmod_query(query, values=True)
    if not query_resp_df.empty:
        gt_data_df = pd.DataFrame([
            {
                'ms': row['ms.value'],
                'ms_name': row['ms_name.value'] if len(str(row['ms_name.value'])) > 0 else row['ms.value'].split('/')[-1],
                'country': row.get('country.value', None),
                'state_or_province': row.get('state_or_province.value', None),
                'loc_wkt': row.get('loc_wkt.value', None),
                'tot_tonnage_measured': float(row['total_tonnage_measured.value']),
                'tot_tonnage_indicated': float(row['total_tonnage_indicated.value']),
                'tot_tonnage_inferred': float(row['total_tonnage_inferred.value']),
                'tot_contained_measured': float(row['total_contained_measured.value']),
                'tot_contained_indicated': float(row['total_contained_indicated.value']),
                'tot_contained_inferred': float(row['total_contained_inferred.value']),
                'total_tonnage': float(row['total_tonnage.value']),
                'total_grade': float(row['total_grade.value'])
            }
            for index, row in query_resp_df.iterrows()
        ])

        gt_df_only = gt_data_df.drop_duplicates()
        gt_df_only.reset_index(drop=True, inplace=True)
        gt_df_only.set_index('ms', inplace=True)
        gt_df_only['info_count'] = gt_df_only[['country', 'state_or_province', 'loc_wkt']].apply(lambda x: ((x != '') & (x.notna())).sum(), axis=1)
        gt_df_only = gt_df_only.sort_values(by='info_count', ascending=False)
        gt_df_only = gt_df_only[~gt_df_only.index.duplicated(keep='first')]
        gt_df_only.drop(columns=['info_count'], inplace=True)
        gt_df_only.to_csv(f'{output_directory}/{commodity}_mineral_sites_to_grade_tonnage.csv', index=True, mode='w')

    # ------------------ Mineral Site to Deposit Type classification results ------------------

    query = '''
       SELECT ?ms ?ms_name ?deposit_name ?deposit_source ?deposit_confidence ?deposit_group ?deposit_environment ?country ?loc_wkt ?state_or_province
       WHERE {

           ?ms :deposit_type_candidate ?deposit_candidate_uri .
           ?deposit_candidate_uri :source ?deposit_source .
           ?deposit_candidate_uri :confidence ?deposit_confidence .
           ?deposit_candidate_uri :normalized_uri [
               rdfs:label ?deposit_name ;
               :deposit_group ?deposit_group ;
               :environment ?deposit_environment ] .

           ?ms :mineral_inventory ?mi .
           OPTIONAL { ?ms rdfs:label|:name ?ms_name . }

           OPTIONAL { 
           ?ms :location_info ?loc .
           OPTIONAL { ?loc :country ?country . }
           OPTIONAL { ?loc :state_or_province ?state_or_province . }
           OPTIONAL { ?loc :location ?loc_wkt . }
           }
           

           ?mi :commodity [ :name ?name ] .
           FILTER(LCASE(STR(?name)) = "%s")
       }
       ''' % (commodity)
    query_resp_df = run_minmod_query(query, values=True)
    if not query_resp_df.empty:
        deposits_data = pd.DataFrame([
            {
                'ms': row['ms.value'],
                'ms_name': row['ms_name.value'] if len(str(row['ms_name.value'])) > 0 else row['ms.value'].split('/')[-1],
                'country': row.get('country.value', None),
                'state_or_province': row.get('state_or_province.value', None),
                'deposit_type': row.get('deposit_name.value', None),
                'deposit_group': row.get('deposit_group.value', None),
                'deposit_environment': row.get('deposit_environment.value', None),
                'deposit_classification_confidence': row.get('deposit_confidence.value', None),
                'deposit_classification_source': row.get('deposit_source.value', None),
                'loc_wkt': row.get('loc_wkt.value', None)
            }
            for index, row in query_resp_df.iterrows()
        ])

        deposits_df = deposits_data.drop_duplicates()
        deposits_df.reset_index(drop=True, inplace=True)
        deposits_df.set_index(['ms', 'deposit_type'], inplace=True)
        deposits_df['info_count'] = deposits_df[['country', 'state_or_province', 'loc_wkt']].apply(lambda x: ((x != '') & (x.notna())).sum(), axis=1)
        deposits_df_ordered = deposits_df.sort_values(by='info_count', ascending=False)
        deposits_df_ordered = deposits_df_ordered[~deposits_df_ordered.index.duplicated(keep='first')]
        deposits_df_ordered.drop(columns=['info_count'], inplace=True)
        deposits_df_ordered.reset_index(inplace=True)
        deposits_df_ordered.to_csv(f'{output_directory}/{commodity}_mineral_sites_to_deposit_types.csv', index=False, mode='w')

    # ------------------ Hyper Site (aggregated group of sites) to Mineral Site ------------------

    # get all Mineral Sites
    query = '''
    SELECT ?ms ?ms_name ?country ?loc_wkt ?state_or_province
    WHERE {

        ?ms :mineral_inventory ?mi .
        OPTIONAL { ?ms rdfs:label|:name ?ms_name . FILTER (STR(?ms_name) != "") }

        OPTIONAL { ?ms :location_info ?loc . 
        OPTIONAL { ?loc :country ?country . FILTER (STR(?country) != "") }
        OPTIONAL { ?loc :state_or_province ?state_or_province . FILTER (STR(?state_or_province) != "") }
        OPTIONAL { ?loc :location ?loc_wkt . FILTER (STR(?loc_wkt) != "") }
        }
        

        OPTIONAL { ?mi :category ?mi_cat . }
        ?mi :commodity [ :name ?name ] .
        FILTER(LCASE(STR(?name)) = "%s")
    }
    ''' % (commodity)
    query_resp_df = run_minmod_query(query, values=True)
    if not query_resp_df.empty:
        sites_df = pd.DataFrame([
            {
                'ms': row['ms.value'],
                'ms_name': row['ms_name.value'] if len(str(row['ms_name.value'])) > 0 else row['ms.value'].split('/')[-1],
                'country': row.get('country.value', None),
                'state_or_province': row.get('state_or_province.value', None),
                'loc_wkt': row.get('loc_wkt.value', None)
            }
            for index, row in query_resp_df.iterrows()
        ])
        sites_df.dropna(subset=['country', 'state_or_province', 'loc_wkt'], how='all', inplace=True)

        df_melted = df_all_sites.melt(id_vars=['group_id'], value_vars=['ms1.value', 'ms2.value'], value_name='ms')

        df_all_sites_groups = df_melted[['ms', 'group_id']].drop_duplicates()
        merged_df_all_sites = pd.merge(sites_df, df_all_sites_groups, how='left', on='ms')

        max_group_id = merged_df_all_sites['group_id'].fillna(0).max()
        merged_df_all_sites['group_id'] = merged_df_all_sites['group_id'].fillna(pd.Series(range(int(max_group_id) + 1, len(merged_df_all_sites) + int(max_group_id) + 1)))
        sorted_df_all_sites_all_dep = merged_df_all_sites.sort_values(by=['group_id', 'ms_name'])

        sorted_df_all_sites_all_dep.reset_index(drop=True, inplace=True)
        sorted_df_all_sites_all_dep.set_index('ms', inplace=True)
        sorted_df_all_sites_all_dep['info_count'] = sorted_df_all_sites_all_dep[['country', 'state_or_province', 'loc_wkt']].apply(lambda x: ((x != '') & (x.notna())).sum(), axis=1)
        sorted_df_all_sites_all_dep = sorted_df_all_sites_all_dep.sort_values(by='info_count', ascending=False)
        sorted_df_all_sites_all_dep = sorted_df_all_sites_all_dep[~sorted_df_all_sites_all_dep.index.duplicated(keep='first')]
        sorted_df_all_sites_all_dep.drop(columns=['info_count'], inplace=True)
        sorted_df_all_sites_all_dep.reset_index(inplace=True)

        sorted_df_all_sites_all_dep.to_csv(f'{output_directory}/{commodity}_mineral_sites_hypersites.csv', index=False, mode='w')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate the TA2 outputs (given a commodity name) from the live MinMod KG using queries")
    parser.add_argument("--commodity", type=str, default='nickel', help="Commodity (default: nickel)", required=True)
    parser.add_argument("--output_directory", type=str, default='output/', help="Output directory for (mineral site grade-tonnages, deposit types, and mineral sites reconciliation (hypersites)")

    args = parser.parse_args()
    main(args)

