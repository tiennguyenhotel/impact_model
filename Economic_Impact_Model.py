import pandas as pd
import base64
import sys
from tabulate import tabulate
# pandas configuration
from IPython.display import HTML
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)

pd.set_option("expand_frame_repr", True)
pd.options.display.float_format = '{:,.3f}'.format
class impact_construction:
    def __init__(self,promised_capital_investment,VA5_Frame,sector_lookup,original_multiples,county=None,state=None,material_share_capex=40,soft_costs_share_capex=10,labor_share_capex=50,labor_cost_split_sal=70, labor_cost_split_ben=30,materials_splits_source=40,materials_splits_captured=80,soft_costs=100,labor_salaries_and_wages=100,labor_benefit_split=35,discount_rate=1.16,inflation=2.8,location_matters_crosswalk=None):
        self.promised_capital_investment = promised_capital_investment
        self.state=state
        self.capex=self.promised_capital_investment/1000000
        self.county=county
        self.VA5_Frame = VA5_Frame
        self.location_matters_crosswalk = location_matters_crosswalk
        self.discount_rate = discount_rate
        self.inflation = inflation
        self.material_share_capex = material_share_capex/100
        self.soft_costs_share_capex = soft_costs_share_capex/100
        self.labor_share_capex = labor_share_capex/100
        self.labor_cost_split_sal = labor_cost_split_sal/100
        self.labor_cost_split_ben = labor_cost_split_ben/100
        self.materials_split_source = materials_splits_source/100
        self.materials_split_captured = materials_splits_captured/100
        self.soft_costs = soft_costs/100
        self.labor_benefit_splits = labor_benefit_split/100
        self.labor_salaries_and_wages = labor_salaries_and_wages/100
        self.categories_first_tab=self.First_Categories()
        self.amount_geography_tab=self.Amount_Capture_In_Geography()
        self.categories_second_tab=self.Second_Categories()
        self.combine=self.Combine_Information()
        self.sector_lookup=sector_lookup
        self.original_multiples=original_multiples
        self.original_multiples_value = self.Original_Multiples_Value()
        self.original_multiples_distribution=self.Original_Multiples_Distribution()
    def Original_Multiples_Distribution(self):

        data_frame=self.original_multiples_value



        titles = ["Output", "Earning", "Employment", "Value-added($M)"]
        json = {}

        array_titles = []
        for i in self.sector_lookup:
            array_titles.append(i)
        array_titles.append("Total")
        for i in titles:
            array = []
            value=self.original_multiples_value[i].values[-1]



            for k in data_frame[i]:
                try:
                    array.append(str(round((k/value)*100,2))+"%")
                except:
                    array.append("nan")

            json[i] = array
        new_data_frame = pd.DataFrame(json)
        new_data_frame.index = array_titles
        return new_data_frame

    def Original_Multiples_Value(self):

        data_frame = self.original_multiples

        titles = ["Output", "Earning", "Employment", "Value-added($M)"]
        json = {}
        array_titles = []
        for i in self.sector_lookup:
            array_titles.append(i)
        array_titles.append("Total")

        for i in titles:
            array = []
            for k in data_frame[i]:
                try:

                    array.append(self.total_amount_capture_in_geography * k)
                except:
                    array.append("nan")

            json[i] = array

        data_frame = pd.DataFrame(json)
        data_frame.index = array_titles
        return data_frame


    def Amount_Capture_In_Geography(self):
        self.amount_geography_first_val=self.materials_split_source*self.materials_split_captured*self.categories_materials
        self.amount_geography_second_val=self.soft_costs*self.categories_soft_costs
        self.amount_geography_third_val=self.labor_salaries_and_wages*self.categories_labor_salaries_wages
        self.amount_geography_fourth_val=self.labor_benefit_splits*self.categories_labor_benefits
        array=[self.amount_geography_first_val,self.amount_geography_second_val,self.amount_geography_third_val,self.amount_geography_fourth_val]
        self.total_amount_capture_in_geography=sum(array)
        array.append(self.total_amount_capture_in_geography)
        data_frame=pd.DataFrame({"Amounts Captured in Geography":array})
        data_frame.index=["Materials","Soft costs","Labor Split Salaries and Wages","Labor Split Benefits","Total"]
        return data_frame
    def First_Categories(self):
        self.categories_materials=self.capex*self.material_share_capex
        self.categories_soft_costs=self.soft_costs_share_capex*self.capex
        self.categories_labor_salaries_wages=self.labor_share_capex*self.capex*self.labor_cost_split_sal
        self.categories_labor_benefits=self.labor_share_capex*self.capex*self.labor_cost_split_ben

        array=[self.categories_materials,self.categories_soft_costs,self.categories_labor_salaries_wages,self.categories_labor_benefits]
        total=sum(array)
        array.append(total)
        data_frame=pd.DataFrame({"Amount":array})
        data_frame.index=["Materials","Soft costs","Labor Split Salaries and Wages","Labor Split Benefits","Total"]
        return data_frame
    def Second_Categories(self):
        data_frame=self.VA5_Frame[self.VA5_Frame["Industry"]=="Construction"]

        array_data=[float(i) for i in data_frame["Direct-effect Employment /6/ (number of jobs)"]]
        self.second_categories_jobs=self.sum(array_data)

        array_data1=[float(i) for i in data_frame["Direct-effect Earnings /5/ (dollars)"]]
        self.second_categories_earnings=self.sum(array_data1)
        main_array=[self.second_categories_jobs,self.second_categories_earnings]
        main_frame=pd.DataFrame({"Multiplier":main_array})
        main_frame.index=["Jobs","Earnings ($M)"]
        return (main_frame)
    def sum(self, data):
        data_return = [i for i in data if str(i) != "nan"]
        sum_data = sum(data_return)
        return sum_data
    def Combine_Information(self):
        data_frame=self.VA5_Frame[self.VA5_Frame["Industry"]=="Construction"]
        array1=[float(i) for i in data_frame["Final-demand Output /1/ (dollars)"]]
        self.output_multiplier=self.sum(array1)
        array2=[float(i) for i in data_frame["Final-demand Employment /3/ (number of jobs)"]]
        self.employment_multiplier=self.sum(array2)
        array3=[float(i) for i in data_frame["Final-demand Earnings /2/ (dollars)"]]
        self.earning_multiplier=self.sum(array3)
        array4=[float(i) for i in data_frame["Final-demand Value-added /4/ (dollars)"]]
        self.value_added_multiplier=self.sum(array4)
        array5=[self.output_multiplier,self.employment_multiplier,self.earning_multiplier,self.value_added_multiplier]
        array6=[float(i*self.total_amount_capture_in_geography) for i in array5]
        direct_array=[self.employment_multiplier/self.second_categories_jobs,self.earning_multiplier/self.second_categories_earnings,1]
        indirect_induce=[self.employment_multiplier-direct_array[0],self.earning_multiplier-direct_array[1],self.output_multiplier-direct_array[2]]
        total_impact_direct_indirect=[direct_array[i]+indirect_induce[i] for i in range(0,3)]
        direct_data_frame=pd.DataFrame({"Direct":direct_array,"Indirect and Induced":indirect_induce,"Total_Impact":total_impact_direct_indirect})
        direct_data_frame.index=["Employment","Earning($M)", "Output(sales,$M)"]
        self.direct_tab=direct_data_frame
        indirect_induce2=[array6[0]-self.total_amount_capture_in_geography,self.total_amount_capture_in_geography*indirect_induce[0],self.total_amount_capture_in_geography*indirect_induce[1],"nan"]
        given_array=[self.total_amount_capture_in_geography,"nan","nan","nan"]
        total_impact_frame=pd.DataFrame({"Given":given_array,"Multiplier":array5,"Total_Impact":array6,"(Indirect and Induced)":indirect_induce2})
        total_impact_frame.index=["Output(sales,$M)","Employment","Earnings","Value-added($M)"]
        self.total_impact_tab=total_impact_frame






class Model:

    def __init__(self,SBSU_Category_Frame,NSF_Frame,Census_SUSB_National_Frame,VA2_Totalmul,VA2_Frame_Output, VA2_Frame_Earning,VA2_Frame_Employment,VA2_Frame_Valueadd,sector_lookup,promised_capital_investment, irs_sector, promised_jobs, promised_wages,attraction_or_relocation,economic_impact_sector):
        self.VA2_Frame_Valueadd=VA2_Frame_Valueadd
        self.irs_sector=irs_sector
        self.promised_jobs=promised_jobs
        self.promised_capital_investment=promised_capital_investment
        if self.promised_jobs < 0:
            raise ("promised_jobs must be greater than 0")
        self.sector_lookup=sector_lookup["Sector"]
        self.VA2_Frame_Earning=VA2_Frame_Earning
        self.VA2_Frame_Output=VA2_Frame_Output

        self.promised_wages=promised_wages
        self.attraction_or_relocation=attraction_or_relocation
        self.economic_impact_sector=str(economic_impact_sector)

        self.SBSU_Category_Frame=SBSU_Category_Frame
        self.VA5_Frame=VA2_Totalmul
        self.promised_jobs_range_fsse=self.SBSU_Category_Frame['SBSU_Category'][self.SUBS_Category_Lookup()]
        self.NSF_Frame=NSF_Frame
        self.VA2_Frame_Employment = VA2_Frame_Employment
        self.rollup_irs_sector=self.rollup_irs()
        self.Census_SUSB_National_Frame=Census_SUSB_National_Frame
        self.estimated_sales_national=self.Estimate_Sales_National()


        self.economic_impact_operation_multiplier = self.Economic_Impact_Operation_Multiplier(["Direct-effect Employment /6/ (number of jobs)", "Direct-effect Earnings /5/ (dollars)","Final-demand Output /1/ (dollars)", "Final-demand Value-added /4/ (dollars)"])

        self.original_multiples = self.Original_Multiples()

        self.multipliers_split_tab = self.Multipliers_Split_Tab()
        self.economic_impact_operation_given=self.Economic_Impact_Operation_Given()
        #
        self.economic_impact_operation_total_impact=self.Economic_Impact_Operation_Total_Impact()
        self.economic_impact_operation_additonal_impact=self.Economic_Impact_Operation_Additional_Impact()
        self.economic_impact_operation=self.Economic_Impact_Operation()
        self.economic_impact_operation2=self.Economic_Impact_Operation2()
        self.original_multiples_value=self.Original_Multiples_Value()
        self.original_multiples_distribution=self.Original_Multiples_Distribution()
    def Original_Multiples_Distribution(self):

        data_frame=self.original_multiples



        titles = ["Output", "Earning", "Employment", "Value-added($M)"]
        json = {}

        array_titles = []
        for i in self.sector_lookup:
            array_titles.append(i)
        array_titles.append("Total")
        for i in titles:
            array = []
            value=self.original_multiples_value[i].values[-1]



            for k in data_frame[i]:
                try:
                    array.append(str(round((k/value)*100,2))+"%")
                except:
                    array.append("nan")

            json[i] = array
        new_data_frame = pd.DataFrame(json)
        new_data_frame.index = array_titles
        return new_data_frame

    def Original_Multiples_Value(self):


        data_frame=self.original_multiples
        titles=["Output", "Earning","Employment","Value-added($M)"]
        json={}
        array_titles=[]
        for i in self.sector_lookup:
            array_titles.append(i)
        array_titles.append("Total")



        for i in titles:
            array = []
            for k in data_frame[i]:
                try:

                    array.append(self.economic_impact_operation_given["Given"][2]*k)
                except:
                    array.append("nan")

            json[i]=array

        data_frame=pd.DataFrame(json)
        data_frame.index=array_titles
        return data_frame


    def Multipliers_Split_Tab(self):
        Jobs=self.sum_original_multiples_employment/self.economic_impact_operation_multiplier["Multiplier"][0]
        Earnings=self.sum_original_multiples_earning/self.economic_impact_operation_multiplier["Multiplier"][1]
        Output=1
        first_array=[Jobs,Earnings,Output]
        indirect_induce=[self.sum_original_multiples_employment-Jobs,self.sum_original_multiples_earning-Earnings,self.sum_original_multiples_output-1]
        self.indirect_induce=indirect_induce
        total_impact=[Jobs+indirect_induce[0],Earnings+indirect_induce[1],Output+indirect_induce[2]]
        data_frame=pd.DataFrame({"Direct":first_array,"Indirect and Induce":indirect_induce,"Total_Impact":total_impact})
        data_frame.index=["Employment","Earnings ($M)","Output(Sales,$M)"]
        return data_frame
    def Economic_Impact_Operation2(self):
        output=float(self.estimated_sales_national/1000000)
        first_array=[output,"nan","nan","nan"]

        array=["Final-demand Output /1/ (dollars)","Final-demand Employment /3/ (number of jobs)","Final-demand Earnings /2/ (dollars)","Final-demand Value-added /4/ (dollars)"]
        multiplier_frame=self.Economic_Impact_Operation_Multiplier(array)
        total_impact=[]

        for i in multiplier_frame["Multiplier"]:
            try:
                total_impact.append(float(output*i))

            except:

                total_impact.append("nan")
        net_addition_impact=[]
        try:
            net_addition_impact.append(float(total_impact[0]-output))
        except:
            net_addition_impact.append("nan")
        try:
            net_addition_impact.append(float(output*self.indirect_induce[0]))
        except:
            net_addition_impact.append("nan")
        try:
            net_addition_impact.append(float(output*self.indirect_induce[1]))

        except:
            net_addition_impact.append("nan")

        net_addition_impact.append("nan")

        data_frame=pd.DataFrame({"Given":first_array,"Multiplier":multiplier_frame["Multiplier"],"Total_Impact":total_impact,"(Indirect and Induced)":net_addition_impact})
        data_frame.index=["Output(sales,$M)","Employment","Earnings","Value-added($M)"]
        data_frame.astype("float")
        return data_frame
    def Original_Multiples(self,data=None):
        if data==None:
            lookup=self.economic_impact_sector
        else:
            lookup=data

        data_frame_output=self.VA2_Frame_Output
        # data_frame_output.columns=data_frame_output.columns.str.lower()
        # data_frame_output.columns = data_frame_output.columns.strip()

        data_frame_output=data_frame_output[data_frame_output["Industry"].isin(self.sector_lookup)]

        index_array=[i for i in self.sector_lookup]
        index_array.append("Total")
        data1=[float(i) for i in data_frame_output[lookup]]
        df1=pd.DataFrame({"Output":data1})
        df1.index=data_frame_output["Industry"]

        self.sum_original_multiples_output=float(self.sum(data_frame_output[lookup]))

        data_frame_earning=self.VA2_Frame_Earning
        data_frame_earning=data_frame_earning[data_frame_earning["Industry"].isin(self.sector_lookup)]

        data2=[float(i) for i in data_frame_earning[lookup]]

        df2=pd.DataFrame({"Earning":data2})

        df2.index = data_frame_earning["Industry"]
        self.sum_original_multiples_earning=float(self.sum(data_frame_earning[lookup]))
        data_frame_employment=self.VA2_Frame_Employment
        data_frame_employment=data_frame_employment[data_frame_employment["Industry"].isin(self.sector_lookup)]
        data3=[float(i) for i in data_frame_employment[lookup]]

        self.sum_original_multiples_employment=float(self.sum(data_frame_employment[lookup]))

        df3 = pd.DataFrame({"Employment": data3})
        df3.index = data_frame_employment["Industry"]

        data_frame_valueadd=self.VA2_Frame_Valueadd

        data_frame_valueadd=data_frame_valueadd[data_frame_valueadd["Industry"].isin(self.sector_lookup)]
        data4=[float(i) for i in data_frame_valueadd[lookup]]
        df4=pd.DataFrame({"Value-added($M)":data4})
        df4.index = data_frame_valueadd["Industry"]
        self.sum_original_multiples_valueadd=float(self.sum(data_frame_valueadd[lookup]))
        #Combine all data
        #joining data frame
        maindf=pd.concat([df1, df2], axis=1)
        maindf=pd.concat([maindf,df3],axis=1)
        maindf=pd.concat([maindf,df4],axis=1)
        # print(maindf)
        newrow=pd.Series(data={"Output":float(self.sum_original_multiples_output),"Earning":float(self.sum_original_multiples_earning),"Employment":float(self.sum_original_multiples_employment),"Value-added($M)":float(self.sum_original_multiples_valueadd)},name="Total")
        main_frame=maindf.append(newrow,ignore_index=False)


        return main_frame

    def Economic_Impact_Operation(self):

        Data_Frame=pd.concat([self.economic_impact_operation_given,self.economic_impact_operation_multiplier],axis=1)
        Data_Frame=pd.concat([Data_Frame,self.economic_impact_operation_total_impact],axis=1)
        Data_Frame=pd.concat([Data_Frame,self.economic_impact_operation_additonal_impact], axis=1)

        index_array=["Employment", "Earnings","Output(sales,$M)","Value-added($M)"]
        Data_Frame.index=index_array
        return Data_Frame


    def Economic_Impact_Operation_Given(self):
        self.earning=(self.promised_jobs*self.promised_wages)/1000000
        self.output_sale=self.estimated_sales_national/1000000
        array=[self.promised_jobs,self.earning,self.output_sale,""]
        data_frame=pd.DataFrame({"Given":array})

        return data_frame

    def Economic_Impact_Operation_Multiplier(self,array1):
        data=self.VA5_Frame
        data=data[data["Industry"]==self.economic_impact_sector]

        try:
            jobs=float(data[array1[0]])
        except:
            jobs="nan"
        try:
            earning=float(data[array1[1]])
        except:
            earning="nan"
        try:
            output=float(data[array1[2]])
        except:
            output="nan"
        try:
            value_added=float(data[array1[3]])
        except:
            value_added="nan"
        array=[jobs,earning,output,value_added]
        data_frame=pd.DataFrame({"Multiplier":array})
        return data_frame

    def Economic_Impact_Operation_Total_Impact(self):
        data=[]
        # data=[round(float(self.economic_impact_operation_multiplier["Multiplier"][i])*float(self.economic_impact_operation_given["Given"][i]),0) for i in range(len(self.economic_impact_operation_given["Given"])-1)]
        for i in range(0,3):
            try:
                val=float(self.economic_impact_operation_multiplier["Multiplier"][i]) * float(self.economic_impact_operation_given["Given"][i])
                data.append(val)
            except:
                data.append("nan")
        try:
            data.append(float(self.economic_impact_operation_multiplier["Multiplier"][3])*float(self.economic_impact_operation_given["Given"][2]))
        except:
            data.append("nan")

        Data_Frame=pd.DataFrame({"Total_Impact":data})
        return Data_Frame
    def Economic_Impact_Operation_Additional_Impact(self):
        data=[]
        for i in range(0,3):
            try:

                data.append(self.economic_impact_operation_total_impact["Total_Impact"][i]-self.economic_impact_operation_given["Given"][i])
            except:
                data.append("nan")

        data.append("nan")
        Data_Frame=pd.DataFrame({"(Indirect and Induced)":data})
        return Data_Frame

    def Estimate_Sales_National(self):
        data=self.Census_SUSB_National_Frame
        #sort
        data=data[data["Relevant IRS sector"]==self.rollup_irs_sector]

        data=data[data["ENTERPRISE EMPLOYMENT SIZE"]==self.promised_jobs_range_fsse]

        data=data["Avg. implied sales"]

        array_data=[float(i) for i in data]

        sum=self.sum(array_data)
        return sum



    def sum(self, data):
        data_return = [i for i in data if str(i) != "nan"]
        sum_data = sum(data_return)
        return sum_data
    def rollup_irs(self):
        data=self.NSF_Frame.set_index("IRS corporation categories")
        return_val=data["Rollup IRS sector"][self.irs_sector]
        return return_val




    def SUBS_Category_Lookup(self):
        new_array=[self.promised_jobs-i for i in self.SBSU_Category_Frame['Number']]

        index_check=self.check_neigbor_zero(new_array)

        return index_check
        # pass
        # find index of the mimum
    def check_neigbor_zero(self,data):
        for i in range(len(data)):
            if (data[i]>0 or data[i]==0) and (data[i+1]<0):
                return i

        return i

class tableau:
    def __init__(self,df1,df2,df3,df4):
        #df1 is for original_multiples_value from economic operations
        #and so on
        self.df1=df1
        self.df2=df2
        self.df3=df3
        self.df4=df4
        self.sector_lookup=self.df1.index
        self.output_detail=self.detail()

    def detail(self):
        dataframe=pd.concat([self.df1,self.df2],axis=1)
        array=["On going operation_"+str(i) for i in dataframe.index]
        dataframe.index=array
        dataframe1=pd.concat([self.df3,self.df4],axis=1)
        array1=["Construction_"+ str(i) for i in dataframe1.index]
        dataframe1.index=array1
        dataframe3=self.df1.add(self.df3,fill_value=0)
        distribution_frame=self.Original_Multiples_Distribution(dataframe3)
        array2=["Total_" + str(i) for i in dataframe3.index]
        concat_frame=pd.concat([dataframe3,distribution_frame],axis=1)
        concat_frame.index=array2
        main_frame=pd.concat([dataframe,dataframe1])
        main_frame=pd.concat([main_frame,concat_frame])


        return main_frame

    def Original_Multiples_Distribution(self,data):

        data_frame = data

        titles = ["Output", "Earning", "Employment", "Value-added($M)"]
        json = {}

        array_titles = [i for i in data.index]

        for i in titles:
            array = []
            value = data[i].values[-1]

            for k in data_frame[i]:
                try:
                    array.append(str(round((k / value) * 100, 2)) + "%")
                except:
                    array.append("nan")

            json[i] = array
        new_data_frame = pd.DataFrame(json)
        new_data_frame.index = array_titles
        return new_data_frame
    def Output_Summary(self,frame1,frame3):
        index=["Ongoing operations","Ongoing operations","Ongoing operations","Ongoing operations","Construction","Construction","Construction","Construction","Total","Total","Total","Total"]
        #only need frame1 and frame3 adding together
        frame1=frame1.fillna(0).replace("nan",0).replace("",0).astype("float")
        frame3=frame3.fillna(0).replace("nan",0).replace("",0).astype("float")
        new_add_frame=frame1.add(frame3,fill_value=0)
        complete_frame=pd.concat([frame1,frame3])
        complete_frame=pd.concat([complete_frame,new_add_frame]).fillna("").replace("nan","").replace(0,"")
        title_colum=pd.DataFrame({"Activity":index})
        index1=complete_frame.index
        title_colum.index=index1
        complete_frame=pd.concat([title_colum,complete_frame],axis=1)

        return complete_frame
        #concat 2 dataframe and drop duplicate


    def csv(self,df, title="Download CSV file", filename="data.csv"):
        csv = df.to_csv()
        b64 = base64.b64encode(csv.encode())
        payload = b64.decode()
        html = '<a download="{filename}" href="data:text/csv;base64,{payload}" target="_blank">{title}</a>'
        html = html.format(payload=payload, title=title, filename=filename)
        return HTML(html)








